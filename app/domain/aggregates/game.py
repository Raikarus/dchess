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
    def __init__(self, players: List[str], piece_behaviour_map: dict):
        self.players = players
        self.current_turn: Color = Color.WHITE
        self.state: GameState = GameState.ONGOING
        self.board: "Board" = self._initialize_board()
        self.move_history: List[Move] = []
        self.current_player = players[0]
        self.current_turn = Color.WHITE
        self.piece_behaviour_map = piece_behaviour_map

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
        possible_moves = self.get_moves_from(move.from_position)
        move_found = False
        for possible_move in possible_moves:
            if (move.from_position, move.to_position) == (possible_move.from_position, possible_move.to_position):
                move = possible_move
                move_found = True
                break
        if not move_found:
            raise ValueError(f"{move} is impossible")
        self.board.move_piece(move)
        self.move_history.append(move)
        self.switch_turn()

    def switch_turn(self):
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE

    def get_moves_from(self, piece_position: "Position") -> List[Move]:
        board = self.board
        piece_type, piece_color = board.get_piece_at(piece_position)
        strategy_provider = self.piece_behaviour_map.get(piece_type)
        if not strategy_provider:
            raise ValueError(f"No strategy for {piece_type}")
        move_patterns = strategy_provider(piece_position)  # создается или берется синглтон
        possible_moves = []
        for move_pattern in move_patterns:
            for i in range(move_pattern.move_vector.length):
                new_piece_position = piece_position + move_pattern.move_vector.dPos * (i + 1)
                attack_position = piece_position + move_pattern.attack_vector.dPos * (i + 1)
                if not board.is_empty(attack_position):
                    target_piece_type, target_piece_color = board.get_piece_at(new_piece_position)
                else:
                    target_piece_type, target_piece_color = None, None
                if board.is_within_bounds(new_piece_position):
                    if target_piece_color is not None and target_piece_color != piece_color:
                        possible_moves += [Move(piece_position, new_piece_position, attack_position)]
                        break
                    if target_piece_color is None and not move_pattern.only_in_attack:
                        possible_moves += [Move(piece_position, new_piece_position)]

        return possible_moves
