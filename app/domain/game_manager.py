from typing import List
from enum import Enum
import torch
from .color import Color
from .move import Move
from .board import Board
from .position import Position
from .pieces import PieceFactory, King


class GameState(Enum):
    ONGOING = 1
    CHECK = 2
    CHECKMATE = 3
    STALEMATE = 4
    DRAW = 5


class GameManager:
    def __init__(self, players: List[str]):
        self.players = players
        self.current_turn: Color = Color.WHITE
        self.state: GameState = GameState.ONGOING
        self.board: "Board" = self._initialize_board()
        self.move_history: List[Move] = []
        self.current_player = players[0]
        self.current_turn = Color.WHITE

    @staticmethod
    def _initialize_board() -> "Board":
        """
        Создание и настройка начальной доски

        :return: объект доски с расставленными фигурами
        """
        board = Board(12, 8, 3)
        start_positions = {
            ("sylf", Color.WHITE): [Position(x, 1, 2) for x in range(0, 11, 2)],
            ("sylf", Color.BLACK): [Position(x, 6, 2) for x in range(0, 11, 2)],
            ("gryphon", Color.WHITE): [Position(2, 0, 2), Position(10, 0, 2)],
            ("gryphon", Color.BLACK): [Position(2, 7, 2), Position(10, 7, 2)],
            ("king", Color.WHITE): [Position(6, 0, 1)],
            ("king", Color.BLACK): [Position(6, 7, 1)]
        }
        for (piece_name, color), positions in start_positions.items():
            board.register_start_positions(piece_name, color, positions)
            for pos in positions:
                piece = PieceFactory.create_piece(piece_name, pos, color)
                board.place_piece(piece)
        return board

    def make_move(self, move: Move) -> bool:
        piece = self.board.get_piece_at(move.from_position)
        if not piece or piece.color != self.current_turn:
            return False  # no piece or wrong color

        valid_moves = self.get_valid_moves(move.from_position)
        if move not in valid_moves:
            return False  # ход недопустим

        self.board.move_piece(move)
        self.move_history.append(move)

        # Проверяем, не приводит ли этот ход к собственному шаху
        if self.is_check(self.current_turn):
            # Отменяем ход
            self.undo_move()
            return False

        # Переключаем ход и обновляем состояние
        self.switch_turn()
        self.state = self.get_game_state()
        self.current_player = self.players[0] if self.current_turn == Color.WHITE else self.players[1]
        return True

    def undo_move(self) -> None:
        if not self.move_history:
            return

        last_move = self.move_history.pop()
        piece = self.board.get_piece_at(last_move.to_position)
        if piece:
            piece.position = last_move.from_position
            self.board._pieces[last_move.from_position] = piece
            del self.board._pieces[last_move.to_position]

        self.switch_turn()
        self.state = self.get_game_state()
        self.current_player = self.players[0] if self.current_turn == Color.WHITE else self.players[1]

    def is_check(self, color: Color) -> bool:
        """
        Проверить, находится ли игрок с указанным цветом под шахом
        :param color: цвет игрока
        :return: True, если шах, иначе False
        """
        pass

    def switch_turn(self) -> None:
        """
        Сменить текущего игрока (ход)
        """
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE

    def get_valid_moves(self, position: Position) -> List[Move]:
        pos = position
        piece = self.board.get_piece_at(pos)
        if not piece or piece.color != self.current_turn:
            return []

        possible_moves = piece.possible_moves(self.board)
        # Фильтруем ходы, которые приводят к собственному шаху
        valid = []
        for move in possible_moves:
            self.board.move_piece(move)
            if not self.is_check(piece.color):
                valid.append(move)
            move_back = Move(move.to_position, move.from_position)
            self.board.move_piece(move_back)
        return valid

    def get_game_state(self) -> GameState:
        if self.is_checkmate():
            return GameState.CHECKMATE
        elif self.is_stalemate():
            return GameState.STALEMATE
        elif self.is_check(self.current_turn):
            return GameState.CHECK
        else:
            return GameState.ONGOING

    def is_position_attacked(self, position: Position, attacker_color: Color) -> bool:
        # Проверить, может ли любая фигура attacker_color атаковать position
        for pos, piece in self.board._pieces.items():
            if piece.color != attacker_color:
                continue
            moves = piece.possible_moves(self.board)
            if any(m.to_position == position for m in moves):
                return True
        return False

    def __str__(self) -> str:
        # Отображаем доску в виде простого текста
        res = f"Ход: {'Белые' if self.current_turn == Color.WHITE else 'Чёрные'}\n"
        res += f"Состояние: {self.state.name}\n"
        for z in range(self.board.depth):
            res += f"Уровень {z}:\n"
            for y in range(self.board.height):
                row = ""
                for x in range(self.board.width):
                    piece = self.board.get_piece_at(Position(x, y, z))
                    if piece:
                        row += type(piece).__name__[0]
                    else:
                        row += "."
                res += row + "\n"
        return res

    def print_move_history(self):
        """
        Вывод всей истории ходов партии в порядке очереди.
        Использует стартовые позиции фигур для идентификации фигур и их последовательных перемещений.
        """
        # Создаем словарь для отслеживания текущих позиций каждой фигуры по ключу (piece_name, color, index)
        piece_positions = {}
        # Располагаем фигуры по стартовым позициям
        for piece_name in ["sylf", "gryphon", "king"]:
            for color in [Color.WHITE, Color.BLACK]:
                start_positions = self.board.get_start_positions_for_piece(piece_name, color)
                for idx, pos in enumerate(start_positions):
                    piece_positions[(piece_name, color, idx)] = pos

        # Инвертируем словарь по позициям для быстрого поиска фигуры по позиции
        position_to_piece = {}
        for key, pos in piece_positions.items():
            position_to_piece[(pos.x, pos.y, pos.z)] = key  # key это (piece_name, color, idx)

        move_list = []
        # Обрабатываем каждый ход из истории
        for move in self.move_history:
            from_key = position_to_piece.get((move.from_position.x, move.from_position.y, move.from_position.z))
            if from_key is None:
                # Если фигура не найдена (например, при переводе в новую позицию после взятия),
                # просто используем координаты (не идеально, но безопасно)
                piece_name, color, idx = "unknown", None, None
            else:
                piece_name, color, idx = from_key

            # Обновляем позицию фигуры после хода
            piece_positions[(piece_name, color, idx)] = move.to_position
            # Обновляем mapping позиции
            del position_to_piece[(move.from_position.x, move.from_position.y, move.from_position.z)]
            position_to_piece[(move.to_position.x, move.to_position.y, move.to_position.z)] = (piece_name, color, idx)

            # Формируем текстовое представление хода
            move_str = f"{color.name} {piece_name} {move.from_position} -> {move.to_position}"
            move_list.append(move_str)

        # Печатаем всю историю ходов
        print("История партии:")
        for idx, mv in enumerate(move_list, 1):
            print(f"{idx}. {mv}")

    def get_all_legal_moves(self, color: Color) -> List[Move]:
        legal_moves = []
        board_copy = self.board._pieces.copy()
        for pos, piece in board_copy.items():
            if piece.color != color:
                continue
            moves = piece.possible_moves(self.board)
            for move in moves:
                self.board.move_piece(move)
                if not self.is_check(piece.color):
                    legal_moves.append(move)
                move_back = Move(move.to_position, move.from_position)
                self.board.move_piece(move_back)
        return legal_moves

    def get_piece_states(self) -> torch.Tensor:
        # Создаем пустой тензор с нулями: 2 цвета, 8x8x8 доска
        states = torch.zeros((2, self.board.width, self.board.height, self.board.depth), dtype=torch.float32)
        for pos, piece in self.board._pieces.items():
            color_idx = 0 if piece.color == Color.WHITE else 1  # Пример индексации цвета
            states[color_idx, pos.x, pos.y, pos.z] = 1.0
        return states

    def get_piece_values(self) -> torch.Tensor:
        values = torch.zeros((self.board.width, self.board.height, self.board.depth), dtype=torch.float32)
        for pos, piece in self.board._pieces.items():
            values[pos.x, pos.y, pos.z] = piece.piece_value
        return values

    def get_reward(self) -> float:
        """
        Возвращает текущее вознаграждение за состояние доски.
        Например:
          +1.0 если игрок победил,
          -1.0 если проиграл,
          0.0 за текущие ходы без окончания.
        Нужно делать проверку фактических условий победы/проигрыша.
        """
        if self.is_checkmate():
            # Предполагаем, что цвет текущего игрока в self.current_player
            # Вознаграждаем если текущий игрок выиграл
            return 1.0
        elif self.is_stalemate():
            return 0.0
        else:
            return 0.0  # или можно добавить оценки, например по материалу

    def is_done(self) -> bool:
        """
        Проверяет, закончена ли партия.
        Есть ли шах и мат, пат, ничья.
        """
        return self.is_checkmate() or self.is_stalemate() or self.is_draw()

    def is_checkmate(self) -> bool:
        king_pos = self.find_king(self.current_turn)
        if not self.is_position_attacked(king_pos, self.opponent_color(self.current_turn)):
            return False  # король не под шахом — нет мата
        legal_moves = self.get_all_legal_moves(self.current_turn)
        if legal_moves:
            return False  # есть ход для выхода из шаха
        return True  # король под шахом, ходов нет — мат

    def is_stalemate(self) -> bool:
        king_pos = self.find_king(self.current_turn)
        if self.is_position_attacked(king_pos, self.opponent_color(self.current_turn)):
            return False  # король под шахом — не пат
        legal_moves = self.get_all_legal_moves(self.current_turn)
        if not legal_moves:
            return True  # нет ходов и нет шаха — пат
        return False

    def is_draw(self) -> bool:
        # Простая заглушка — можно добавить правила 50 ходов, повторения и т.п.
        return False

    def find_king(self, color: Color) -> Position:
        # Найти позицию короля указанного цвета
        for pos, piece in self.board._pieces.items():
            if piece.color == color and isinstance(piece, King):
                return pos
        print(str(self))
        self.print_move_history()
        raise ValueError("Король не найден")

    def opponent_color(self, color: Color) -> Color:
        # Вернуть цвет противника
        return Color.BLACK if color == Color.WHITE else Color.WHITE
