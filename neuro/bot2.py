import random
from collections import deque

import numpy as np
import requests
import torch
import torch.nn as nn
import torch.optim as optim

API_BASE = "http://127.0.0.1:8000/api/game"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Упрощённое NN для Q-learning (пример)
class ChessQNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(ChessQNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 1)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)


# Преобразование позиции хода в вектор (статический упрощённый пример)
def move_to_vector(move):
    # Пример кодировки: координаты from_position и to_position нормализованы к [0..1]
    return np.array([
        move['from_position']['x'] / 11,  # width=12 -1
        move['from_position']['y'] / 7,  # height=8 -1
        move['from_position']['z'] / 2,  # depth=3 -1
        move['to_position']['x'] / 11,
        move['to_position']['y'] / 7,
        move['to_position']['z'] / 2,
    ], dtype=np.float32)


class RLChessBot:
    def __init__(self):
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = ChessQNetwork(6, 100).to(DEVICE)
        self.load_weights("model_weights.pth")
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.MSELoss()

        self.prev_board = None
        self.prev_pieces_count = {}

    def load_weights(self, path):
        try:
            self.model.load_state_dict(torch.load(path, map_location=DEVICE))
            self.model.eval()
            print(f"Model weights loaded from {path}")
        except FileNotFoundError:
            print(f"No pre-trained weights found at {path}, starting fresh.")

    def save_model(self, path="model_weights.pth"):
        torch.save(self.model.state_dict(), path)
        print(f"Model saved to {path}")

    def create_game(self):
        resp = requests.post(f"{API_BASE}/new")
        if resp.status_code == 200:
            print("Game created")
            self.prev_board = None
            self.prev_pieces_count = {}
        else:
            raise RuntimeError("Failed to create game")

    def get_state(self):
        resp = requests.get(f"{API_BASE}/state")
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError("Failed to get game state")

    def get_moves(self):
        resp = requests.get(f"{API_BASE}/moves")
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError("Failed to get moves")

    def make_move(self, move):
        move_data = {
            "from_position": move["from_position"],
            "to_position": move["to_position"],
        }
        resp = requests.post(f"{API_BASE}/make_move", json=move_data)
        if resp.status_code != 200:
            raise RuntimeError(f"Move rejected: {resp.json()}")

    def count_pieces(self, board):
        """
        Считает количество фигур у каждой стороны: словарь вида
        { 'white': кол-во, 'black': кол-во }
        """
        pieces_count = {'white': 0, 'black': 0}
        for key, (ptype, color, pos) in board['pieces'].items():
            color = board["pieces"][key]['color']
            pieces_count[color] = pieces_count.get(color, 0) + 1
        return pieces_count

    def compute_reward(self, prev_pieces_count, current_pieces_count, done, game_state, move_count):
        reward = 0

        # Считаем съеденные фигуры этим ходом
        if prev_pieces_count:
            # Съедено у противника — увеличение их потерь
            killed_white = prev_pieces_count.get('white', 0) - current_pieces_count.get('white', 0)
            killed_black = prev_pieces_count.get('black', 0) - current_pieces_count.get('black', 0)

            # Если бот ходит за white, положим съедание фигур black – награда
            # потери своих фигур – штраф
            reward += killed_black - killed_white

        # За победу/поражение
        if done:
            if game_state == "WHITE_WON":
                reward += 10 if self.current_turn == 'white' else -10
            elif game_state == "BLACK_WON":
                reward += 10 if self.current_turn == 'black' else -10
            elif game_state == "DRAW":
                reward += 0  # ничья без бонусов

        # Штраф за длину партии (чтобы побуждать выигрывать быстрее)
        reward -= 0.01 * move_count

        return reward

    def choose_action(self, moves):
        states = np.array([move_to_vector(mv) for mv in moves])
        states_tensor = torch.tensor(states, dtype=torch.float32).to(DEVICE)
        with torch.no_grad():
            q_values = self.model(states_tensor).cpu().numpy()
            q_values = np.squeeze(q_values)

        if np.random.rand() <= self.epsilon:
            chosen_idx = random.randrange(len(moves))
            return moves[chosen_idx], chosen_idx
        else:
            temperature = 1.0
            exp_q = np.exp(q_values / temperature)
            probs = exp_q / np.sum(exp_q)
            chosen_idx = np.random.choice(len(moves), p=probs)
            return moves[chosen_idx], chosen_idx

    def remember(self, state, action_idx, reward, next_state, done):
        self.memory.append((state, action_idx, reward, next_state, done))

    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)

        for state, action_idx, reward, next_state, done in batch:
            state_tensor = torch.tensor(state, dtype=torch.float32).to(DEVICE)

            target = reward
            if next_state is not None and not done:
                next_state_tensor = torch.tensor(next_state, dtype=torch.float32).to(DEVICE)
                target = reward + self.gamma * torch.max(self.model(next_state_tensor)).item()

            target_f = self.model(state_tensor)
            if action_idx is not None and action_idx >= 0 and action_idx < target_f.shape[0]:
                target_f[action_idx] = target
            else:
                continue

            loss = self.loss_fn(self.model(state_tensor), target_f.unsqueeze(0))
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def train_self_play(self, episodes=1000):
        for e in range(episodes):
            self.create_game()
            done = False
            move_count = 0

            prev_state = self.get_state()
            self.prev_board = prev_state['board']
            self.prev_pieces_count = self.count_pieces(prev_state['board_obj'])
            self.current_turn = prev_state['current_turn']

            while not done:
                moves = self.get_moves()
                if not moves:
                    print("Game finished")
                    done = True
                    break

                action, action_idx = self.choose_action(moves)
                try:
                    self.make_move(action)
                except RuntimeError as err:
                    print("Move error:", err)
                    done = True
                    break

                move_count += 1
                state = self.get_state()
                self.current_turn = state['current_turn']

                current_pieces_count = self.count_pieces(state['board_obj'])

                done = state["game_state"] != "ONGOING"

                reward = self.compute_reward(self.prev_pieces_count, current_pieces_count, done, state["game_state"],
                                             move_count)

                self.remember(move_to_vector(action), action_idx, reward, None if done else move_to_vector(action),
                              done)

                self.prev_pieces_count = current_pieces_count
                self.prev_board = state['board']

                self.replay()

            print(f"Episode {e + 1}/{episodes} finished, epsilon: {self.epsilon:.2f}")

        self.save_model()


if __name__ == "__main__":
    bot = RLChessBot()
    bot.train_self_play(episodes=10)  # Запуск для 10 партий, можно увеличить
