from typing import List
from enum import Enum
from app.domain.color import Color
from app.domain.board import Board
from app.domain.value_objects import BoardGeometry, PieceType, Position, Move
from copy import deepcopy


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
            (PieceType.KING, Color.WHITE): [Position(6, 0, 1)],
            (PieceType.KING, Color.BLACK): [Position(6, board_geometry.height - 1, 1)],
            (PieceType.GRYPHON, Color.WHITE): [Position(2, 0, 2), Position(board_geometry.width - 3, 0, 2)],
            (PieceType.GRYPHON, Color.BLACK): [Position(2, board_geometry.height - 1, 2),
                                               Position(board_geometry.width - 3, board_geometry.height - 1, 2)],
            (PieceType.DRAGON, Color.WHITE): [Position(6, 0, 2)],
            (PieceType.DRAGON, Color.BLACK): [Position(6, board_geometry.height - 1, 2)],
            (PieceType.WARRIOR, Color.WHITE): [Position(i, 1, 1) for i in range(board_geometry.width)],
            (PieceType.WARRIOR, Color.BLACK): [Position(i, 6, 1) for i in range(board_geometry.width)],
            (PieceType.HERO, Color.WHITE): [Position(2, 0, 1), Position(board_geometry.width - 3, 0, 1)],
            (PieceType.HERO, Color.BLACK): [Position(2, board_geometry.height - 1, 1),
                                            Position(board_geometry.width - 3, board_geometry.height - 1, 1)],
            (PieceType.OLIPHANT, Color.WHITE): [Position(0, 0, 1), Position(board_geometry.width - 1, 0, 1)],
            (PieceType.OLIPHANT, Color.BLACK): [Position(0, board_geometry.height - 1, 1),
                                                Position(board_geometry.width - 1, board_geometry.height - 1, 1)],
            (PieceType.UNICORN, Color.WHITE): [Position(1, 0, 1), Position(board_geometry.width - 2, 0, 1)],
            (PieceType.UNICORN, Color.BLACK): [Position(1, board_geometry.height - 1, 1),
                                               Position(board_geometry.width - 2, board_geometry.height - 1, 1)],
            (PieceType.THIEF, Color.WHITE): [Position(3, 0, 1), Position(board_geometry.width - 4, 0, 1)],
            (PieceType.THIEF, Color.BLACK): [Position(3, board_geometry.height - 1, 1),
                                             Position(board_geometry.width - 4, board_geometry.height - 1, 1)],
            (PieceType.CLERIC, Color.WHITE): [Position(4, 0, 1)],
            (PieceType.CLERIC, Color.BLACK): [Position(4, board_geometry.height - 1, 1)],
            (PieceType.MAGE, Color.WHITE): [Position(5, 0, 1)],
            (PieceType.MAGE, Color.BLACK): [Position(5, board_geometry.height - 1, 1)],
            (PieceType.PALADIN, Color.WHITE): [Position(7, 0, 1)],
            (PieceType.PALADIN, Color.BLACK): [Position(7, board_geometry.height - 1, 1)],
            (PieceType.DWARF, Color.WHITE): [Position(i, 1, 0) for i in range(1, board_geometry.width, 2)],
            (PieceType.DWARF, Color.BLACK): [Position(i, board_geometry.height - 2, 0) for i in
                                             range(1, board_geometry.width, 2)],
            (PieceType.BASILISK, Color.WHITE): [Position(3, 0, 0), Position(board_geometry.width - 3, 0, 0)],
            (PieceType.BASILISK, Color.BLACK): [Position(3, board_geometry.height - 1, 0),
                                                Position(board_geometry.width - 3, board_geometry.height - 1, 0)],
        }

        board = Board(board_geometry, starting_positions)

        for (piece_type, color), positions_array in starting_positions.items():
            for position in positions_array:
                board.place_piece(piece_type, color, position)

        return board

    def move_piece(self, move: Move) -> None:
        if self.state != GameState.ONGOING and self.state != GameState.CHECK:
            raise ValueError(f"Game is over: {self.state}")
        piece_info = self.board.get_piece_at(move.from_position)
        if piece_info is None:
            raise ValueError(f"No piece at {move.from_position}")

        piece_type, piece_color = piece_info

        if piece_color != self.current_turn:
            raise ValueError(f"It's {self.current_turn} turn, cannot move piece of color {piece_color}")

        if move.from_position.z == 1:
            enemy_position = Position(move.from_position.x, move.from_position.y, 0)
            enemy_unit = self.board.get_piece_at(enemy_position)
            if enemy_unit:
                enemy_type, enemy_color = enemy_unit
                if enemy_type == PieceType.BASILISK and enemy_color != piece_type:
                    raise ValueError(f"Ooops, this piece is frozen by Basilisk")

        possible_moves = self.get_moves_from(self.board, move.from_position)
        move_found = False
        for possible_move in possible_moves:
            if (move.from_position, move.to_position) == (possible_move.from_position, possible_move.to_position):
                move = possible_move
                move_found = True
                break
        if not move_found:
            raise ValueError(f"{move} is impossible")

        board_copy = deepcopy(self.board)
        board_copy.move_piece(move)

        if self.is_in_check(board_copy, piece_color):
            raise ValueError("Move would put or leave king in check")

        self.board.move_piece(move)
        self.move_history.append(move)
        self.try_promote_piece(move.to_position)

        self.switch_turn()

        self.update_game_state()

    def is_in_check(self, board: Board, color: Color) -> bool:
        king_position = None
        for pos, (ptype, pcolor) in board.pieces.items():
            if ptype == PieceType.KING and pcolor == color:
                king_position = pos
                break
        if king_position is None:
            return True

        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        for pos, (ptype, pcolor) in board.pieces.items():
            if pcolor == opponent_color:
                moves = self.get_moves_from(board, pos)
                for move in moves:
                    if move.attack_position == king_position:
                        return True
        return False

    def is_checkmate(self, color: Color) -> bool:
        if not self.is_in_check(self.board, color):
            return False

        for pos, (ptype, pcolor) in self.board.pieces.items():
            if pcolor == color:
                moves = self.get_moves_from(self.board, pos)
                for move in moves:
                    board_copy = deepcopy(self.board)
                    board_copy.move_piece(move)
                    if not self.is_in_check(board_copy, color):
                        return False
        return True

    def is_stalemate(self, color: Color) -> bool:
        if self.is_in_check(self.board, color):
            return False
        for pos, (ptype, pcolor) in self.board.pieces.items():
            if pcolor == color:
                moves = self.get_moves_from(self.board, pos)
                for move in moves:
                    board_copy = deepcopy(self.board)
                    board_copy.move_piece(move)
                    if not self.is_in_check(board_copy, color):
                        return False
        return True

    def update_game_state(self):
        if self.is_checkmate(self.current_turn):
            self.state = GameState.CHECKMATE
        elif self.is_stalemate(self.current_turn):
            self.state = GameState.STALEMATE
        elif self.is_in_check(self.board, self.current_turn):
            self.state = GameState.CHECK
        else:
            self.state = GameState.ONGOING

    def undo_move(self):
        if not self.move_history:
            raise ValueError("No moves to undo")
        last_move = self.move_history.pop()
        self.board = self._initialize_board()
        for move in self.move_history:
            self.board.move_piece(move)
        self.switch_turn()  # Отмена хода меняет текущего игрока обратно

    def switch_turn(self):
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE

    def get_moves_from(self, board: "Board", piece_position: "Position") -> List[Move]:
        piece_type, piece_color = board.get_piece_at(piece_position)
        strategy_provider = self.piece_behaviour_map.get(piece_type)
        if not strategy_provider:
            raise ValueError(f"No strategy for {piece_type}")
        move_patterns = strategy_provider(piece_position, self.board)
        possible_moves = []
        for move_pattern in move_patterns:
            for i in range(move_pattern.move_vector.length):
                new_piece_position = piece_position + move_pattern.move_vector.dPos * (i + 1)
                attack_position = piece_position + move_pattern.attack_vector.dPos * (i + 1)
                if not board.is_empty(attack_position) and attack_position != piece_position:
                    target_piece_type, target_piece_color = board.get_piece_at(attack_position)
                else:
                    target_piece_type, target_piece_color = None, None

                if board.is_within_bounds(new_piece_position):
                    if target_piece_color is not None and target_piece_color != piece_color:
                        possible_moves += [Move(piece_position, new_piece_position, attack_position)]
                        break
                    if target_piece_color is not None and target_piece_color == piece_color:
                        break
                    if target_piece_color is None and not move_pattern.only_in_attack:
                        if board.is_empty(new_piece_position):
                            possible_moves += [Move(piece_position, new_piece_position)]
                        else:
                            break

        return possible_moves

    def try_promote_piece(self, position: Position) -> None:
        piece_type, piece_color = self.board.get_piece_at(position)
        strategy_provider = self.piece_behaviour_map.get(piece_type)
        if not strategy_provider:
            raise ValueError(f"No strategy for {piece_type}")
        is_promote = strategy_provider.is_promote(self.board, position)
        if is_promote:
            promoted_piece_type = strategy_provider.get_promote_type()
            self.board.place_piece(promoted_piece_type, piece_color, position)
