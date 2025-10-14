from typing import List
from enum import Enum
from .color import Color
from .move import Move
from .board import Board
from .position import Position
from .pieces import PieceFactory

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

    def _initialize_board(self) -> "Board":
        """
        Создание и настройка начальной доски

        :return: объект доски с раставленными фигурами
        """
        board = Board(12, 8, 3)
        symbols = {
            "sylf": "😇",
            "gryphon": "🦅"
        }
        start_positions = {
            ("sylf", Color.WHITE): [Position(x, 1, 2) for x in range(0, 11, 2)],
            ("sylf", Color.BLACK): [Position(x, 6, 2) for x in range(0, 11, 2)],
            ("gryphon", Color.WHITE): [Position(2, 0, 2), Position(10, 0, 2)],
            ("gryphon", Color.BLACK): [Position(2, 7, 2), Position(10, 7, 2)]
        }
        for (piece_name, color), positions in start_positions.items():
            board.register_start_positions(piece_name, color, positions)
            for pos in positions:
                piece = PieceFactory.create_piece(piece_name, pos, color, symbols[piece_name])
                board.place_piece(piece)
        return board

    def make_move(self, move: Move) -> bool:
        """

        :param move: объект с описанием хода
        :return: True, если ход выполнен успешно, иначе False
        """
        pass

    def undo_move(self) -> None:
        """
        Отменить последний ход, обновить состояние игры
        """
        pass

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

    def get_valid_moves(self, position: str) -> List[Move]:
        """
        Получить список доступных ходов для фигуры на определенной позиции
        :param position:
        :return:
        """

    def get_game_state(self) -> GameState:
        """
        Получить текеущее состояние игры (игра продолжается, шах, мат и т.д.)
        :return:
        """
        pass

    def __str__(self) -> str:
        """Читаемое текстовое представление доски и текущего состояния"""

        pass