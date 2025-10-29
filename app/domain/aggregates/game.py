from typing import List
from enum import Enum
from app.domain.color import Color
from app.domain.board import Board
from app.domain.value_objects import BoardGeometry, PieceType, Position, Move


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
        self.board: "Board" = self._initialize_board()
        self.move_history: List[Move] = []
        self.current_player = players[0]
        self.current_turn = Color.WHITE

    @staticmethod
    def _initialize_board():
        board_geometry = BoardGeometry(width=12, height=8, depth=3)

        starting_positions = {
            (PieceType.SYLPH, Color.WHITE): [Position(x, 1, 2) for x in range(0, board_geometry.width, 2)],
            (PieceType.SYLPH, Color.BLACK): [Position(x, board_geometry.height - 2, 2) for x in
                                             range(0, board_geometry.width, 2)],
            (PieceType.KING, Color.WHITE): [Position(6, 0, 1)]
        }

        board = Board(board_geometry, starting_positions)

        for (piece_type, color), positions_array in starting_positions.items():
            for position in positions_array:
                board.place_piece(piece_type, color, position)

        return board

    def move_piece(self, move: Move) -> None:
        captured = self.board.move_piece(move)

        self.move_history.append(move)
        # Можно добавить обработку смены хода, проверку шаха, мата и т.п.
        self.switch_turn()

    def switch_turn(self):
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
