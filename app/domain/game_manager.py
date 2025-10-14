from typing import List
from enum import Enum
from .color import Color
from .move import Move


class GameState(Enum):
    ONGOING = 1
    CHECK = 2
    CHECKMATE = 3
    STALEMATE = 4
    DRAW = 5


class Game:
    def __init__(self, players: List[str]):
        self.players = players
        self.current_turn: Color = Color.WHITE
        self.state: GameState = GameState.ONGOING
        self.board = self._initialize_board()
        self.move_history: List[Move] = []

    def _initialize_board(self) -> "Board":
        """
        Создание и настройка начальной доски

        :return: объект доски с раставленными фигурами
        """
        pass

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