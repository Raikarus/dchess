import time

import numpy as np
import requests
import torch
import torch.nn as nn

API_BASE = "http://127.0.0.1:8000/api/game"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ChessQNetwork(nn.Module):
    def __init__(self, input_size, output_size=100):
        super(ChessQNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, output_size)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)


def move_to_vector(move):
    return np.array([
        move['from_position']['x'] / 11,
        move['from_position']['y'] / 7,
        move['from_position']['z'] / 2,
        move['to_position']['x'] / 11,
        move['to_position']['y'] / 7,
        move['to_position']['z'] / 2,
    ], dtype=np.float32)


class RLBotPolling:
    def __init__(self, model_path):
        self.model = ChessQNetwork(6).to(DEVICE)
        self.model.load_state_dict(torch.load(model_path, map_location=DEVICE))
        self.model.eval()
        self.game_id = None

    def create_game(self):
        resp = requests.post(f"{API_BASE}/new")
        resp.raise_for_status()
        self.game_id = resp.json().get("game_id")
        print("Game started, ID:", self.game_id)

    def get_game_state(self):
        resp = requests.get(f"{API_BASE}/state")
        resp.raise_for_status()
        return resp.json()

    def get_moves(self):
        resp = requests.get(f"{API_BASE}/moves")
        resp.raise_for_status()
        return resp.json()

    def make_move(self, move):
        req = {
            "from_position": move["from_position"],
            "to_position": move["to_position"],
        }
        resp = requests.post(f"{API_BASE}/make_move", json=req)
        resp.raise_for_status()
        print(f"Bot moved from {move['from_position']} to {move['to_position']}")

    def bot_choose_move(self, moves):
        vectors = np.array([move_to_vector(m) for m in moves])
        inputs = torch.tensor(vectors, dtype=torch.float32).to(DEVICE)
        with torch.no_grad():
            q_vals = self.model(inputs).cpu().numpy()
        best_idx = q_vals[:, 0].argmax()
        return moves[best_idx]

    def poll_and_move(self):
        while True:
            state = self.get_game_state()
            game_status = state.get("game_state", "ONGOING")
            if game_status != "ONGOING" and game_status != "CHECK":
                print(f"Game ended with status: {game_status}. Bot is exiting.")
                break

            current_turn = state.get("current_turn")
            if current_turn == "BLACK":  # Предполагаем, что бот играет за чёрных
                moves = self.get_moves()
                if not moves:
                    print("No moves available, game may be over.")
                    break
                move = self.bot_choose_move(moves)
                self.make_move(move)
            else:
                print(f"Waiting for human, current turn: {current_turn}")
            time.sleep(1)


if __name__ == "__main__":
    bot = RLBotPolling("model_weights.pth")
    bot.create_game()  # создаём новую игру
    bot.poll_and_move()  # бот запускает постоянную проверку хода и делает ход, когда очередь его
