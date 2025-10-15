from typing import List
from .piece import Piece, register_piece
from ..position import Position
from ..move import Move
from ..color import Color


@register_piece("sylf")
class Sylf(Piece):

    def possible_moves(self, board: "Board") -> List["Move"]:
        moves = []
        curr_pos = self.position
        x, y, z = curr_pos.x, curr_pos.y, curr_pos.z

        if z == 2:
            forward_y = y + 1 if self.color == Color.WHITE else y - 1
            diag_positions = [
                Position(x - 1, forward_y, 2),
                Position(x + 1, forward_y, 2)
            ]
            for pos in diag_positions:
                if board.is_empty(pos):
                    moves.append(Move(curr_pos, pos))
            check_pos = [
                Position(x, y + 1 if self.color == Color.WHITE else y - 1, z),
                Position(x, y, z - 1)
            ]
            for pos in check_pos:
                target_piece = board.get_piece_at(pos)
                if target_piece and target_piece.color != self.color:
                    moves.append(Move(curr_pos, pos, is_capture=True))

        elif z == 1:
            above_pos = Position(x, y, z + 1)
            if board.is_empty(above_pos):
                moves.append(Move(curr_pos, above_pos))

            for pos in board.get_start_positions_for_piece('sylf', self.color):
                if board.is_empty(pos):
                    moves.append(Move(curr_pos, pos))
        moves = [move for move in moves if board.is_within_bounds(move.to_position)]
        return moves

    def can_promote(self) -> bool:
        return False
