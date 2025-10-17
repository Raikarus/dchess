import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from app.domain import GameManager, Move, Color


class PolicyNN(nn.Module):
    def __init__(self):
        super(PolicyNN, self).__init__()
        input_size = 2 * 12 * 8 * 3 * 2  # состояния + ценности, два "канала" игроков
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 12 * 8 * 3)  # выход — вероятности хода в любую клетку

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return torch.softmax(x, dim=1)


def select_action(policy_net, state, game_manager):
    probs = policy_net(state)
    m = Categorical(probs)
    while True:
        action_idx = m.sample()  # индекс хода
        # Восстановим позиции (простейший пример – ходы представлены индексами)
        moves = game_manager.get_all_legal_moves(game_manager.current_turn)
        if not moves:
            return None, None  # нет ходов
        # Ограничиваем выбор ходами с известным индексом
        # Обычно нужна карта соответствия между индексов и ходами.
        # Здесь простая стратегия: выбираем случайный ход из легальных
        # Для примера просто возвращаем случайный ход из moves
        move = moves[action_idx % len(moves)]  # модуль для ограничения
        if move in moves:
            break
    return move, m.log_prob(action_idx)


def state_from_board(game_manager):
    piece_states = game_manager.get_piece_states()  # (2,8,8,8)
    piece_values = game_manager.get_piece_values()  # (8,8,8)
    # Нужно привести piece_values к размеру (2,8,8,8) для конкатенации
    piece_values_exp = torch.stack([piece_values, piece_values], dim=0)
    state = torch.cat([piece_states.unsqueeze(0), piece_values_exp.unsqueeze(0)], dim=1)
    return state.float()


def train(policy_net_1, policy_net_2, game_manager, optimizer_1, optimizer_2, episodes=100):
    for episode in range(episodes):
        game_manager.__init__(game_manager.players)  # сброс игровой доски и состояния
        log_probs_1 = []
        log_probs_2 = []
        rewards_1 = []
        rewards_2 = []
        done = False
        prev_pieces_count = {Color.WHITE: len(game_manager.board._pieces), Color.BLACK: len(game_manager.board._pieces)}
        while not done:
            current_net = policy_net_1 if game_manager.current_turn == Color.WHITE else policy_net_2
            current_optimizer = optimizer_1 if game_manager.current_turn == Color.WHITE else optimizer_2

            state = state_from_board(game_manager)
            move, log_prob = select_action(current_net, state, game_manager)
            if move is None:
                # Нет ходов - игра закончена
                break

            piece_before_move = game_manager.board.get_piece_at(move.from_position)
            target_piece = game_manager.board.get_piece_at(move.to_position)

            succeeded = game_manager.make_move(move)
            if not succeeded:
                # Если ход недопустим, то минус маленький штраф и продолжаем
                if game_manager.current_turn == Color.WHITE:
                    rewards_1.append(-0.1)
                else:
                    rewards_2.append(-0.1)
                continue

            # Рассчитать вознаграждение за ход
            reward = -0.01  # штраф за ход

            # Поедание фигуры противника
            if target_piece is not None and target_piece.color != piece_before_move.color:
                reward += target_piece.piece_value  # поощряем по стоимости съеденной фигуры

            # Потеря своей фигуры (если ход приводит к шаху — ход откатывается, так что учтено)
            # Можно сравнивать кол-во фигур на доске до и после
            current_pieces_count = len(game_manager.board._pieces)
            if current_pieces_count < prev_pieces_count[game_manager.opponent_color(game_manager.current_turn)]:
                # Потеря фигуры у соперника уже учтена выше, здесь проверим у себя
                pass  # не надо, т.к. потери соперника = поедание

            prev_pieces_count = {Color.WHITE: sum(1 for p in game_manager.board._pieces.values() if p.color == Color.WHITE),
                                 Color.BLACK: sum(1 for p in game_manager.board._pieces.values() if p.color == Color.BLACK)}

            # Если игра закончилась - награды за победу/поражение
            if game_manager.is_done():
                if game_manager.is_checkmate():
                    if game_manager.current_turn == piece_before_move.color:
                        reward += -1.0  # текущий игрок матован — проигрыш
                    else:
                        reward += 1.0  # соперник получил мат — выигрыш
                elif game_manager.is_draw() or game_manager.is_stalemate():
                    reward += 0.0  # ничья

                done = True

            # Добавляем логи и награды
            if game_manager.current_turn == Color.WHITE:
                log_probs_1.append(log_prob)
                rewards_1.append(reward)
            else:
                log_probs_2.append(log_prob)
                rewards_2.append(reward)

        # Обновление политик для игрока 1
        if log_probs_1:
            update_policy(log_probs_1, rewards_1, optimizer_1)

        # Обновление политик для игрока 2
        if log_probs_2:
            update_policy(log_probs_2, rewards_2, optimizer_2)

        print(f"Episode {episode + 1} finished.")


def update_policy(log_probs, rewards, optimizer):
    R = 0
    returns = []
    for r in reversed(rewards):
        R = r + 0.99 * R
        returns.insert(0, R)
    returns = torch.tensor(returns)
    returns = (returns - returns.mean()) / (returns.std() + 1e-9)

    loss = 0
    for log_prob, R in zip(log_probs, returns):
        loss += -log_prob * R

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


# Пример запуска
policy_net_1 = PolicyNN()
policy_net_2 = PolicyNN()
optimizer_1 = optim.Adam(policy_net_1.parameters(), lr=1e-3)
optimizer_2 = optim.Adam(policy_net_2.parameters(), lr=1e-3)

game_manager = GameManager(["p1", "p2"])
train(policy_net_1, policy_net_2, game_manager, optimizer_1, optimizer_2, episodes=100)
