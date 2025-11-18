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
        self.fc3 = nn.Linear(256, output_size)

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
        self.gamma = 0.95  # дисконтирование
        self.epsilon = 1.0  # вероятность случайного хода
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001

        # Пусть размер входа - 6 (кодировка хода), выход=максимальное число ходов ~100 (гипотеза)
        # В реальной задачи надо по-другому строить состояниe доски и действие
        self.model = ChessQNetwork(6, 100).to(DEVICE)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.MSELoss()

    def save_model(self, path="model_weights.pth"):
        torch.save(self.model.state_dict(), path)
        print(f"Model saved to {path}")

    def create_game(self):
        resp = requests.post(f"{API_BASE}/new")
        if resp.status_code == 200:
            print("Game created")
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

    def choose_action(self, moves):
        if np.random.rand() <= self.epsilon:
            return random.choice(moves)
        # Предположим, что для каждого хода построим вектор и вычислим Q-values, выберем максимальный
        states = np.array([move_to_vector(mv) for mv in moves])
        states_tensor = torch.tensor(states, dtype=torch.float32).to(DEVICE)
        with torch.no_grad():
            q_values = self.model(states_tensor)
        best_idx = torch.argmax(q_values[:, 0]).item()
        return moves[best_idx]

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in batch:
            target = reward
            if next_state is not None and not done:
                next_state_tensor = torch.tensor(next_state, dtype=torch.float32).to(DEVICE)
                target = reward + self.gamma * torch.max(self.model(next_state_tensor)).item()
            state_tensor = torch.tensor(state, dtype=torch.float32).to(DEVICE)
            target_f = self.model(state_tensor)
            target_f[0] = target  # При необходимости подставьте индекс действия

            loss = self.loss_fn(self.model(state_tensor), target_f)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def train_self_play(self, episodes=1000):
        for e in range(episodes):
            self.create_game()
            done = False

            while not done:
                state = self.get_state()
                moves = self.get_moves()
                if not moves:
                    print("Game finished")
                    done = True
                    break
                action = self.choose_action(moves)
                try:
                    self.make_move(action)
                except RuntimeError as err:
                    print("Move error:", err)
                    done = True
                    break

                # В упрощении предполагаем награду = 0 за каждый ход
                reward = 0
                next_state = self.get_state()
                # Условное завершение при полной или ничейной игре (на основе статуса)
                done = next_state["game_state"] != "ONGOING"
                self.remember(move_to_vector(action), 0, reward, None, done)  # next_state упрощён

                self.replay()

            print(f"Episode {e + 1}/{episodes} finished, epsilon: {self.epsilon:.2f}")
        self.save_model()  # сохранение после всех эпизодов


if __name__ == "__main__":
    bot = RLChessBot()
    bot.train_self_play(episodes=10)  # Запуск для 10 партий, можно увеличить
