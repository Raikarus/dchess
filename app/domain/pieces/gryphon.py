from typing import List
from .piece import Piece, register_piece
from ..position import Position
from ..move import Move
from ..color import Color


@register_piece("gryphon")
class Gryphon(Piece):
    def possible_moves(self, board: "Board") -> List["Move"]:
        moves = []
        curr_pos = self.position
        x, y, z = curr_pos.x, curr_pos.y, curr_pos.z

        if z == 2:
            move_positions = [
                Position(x + i, y + j, 2) for i, j in [(3, 2), (2, 3), (-3, 2), (-3, -2), (-2, -3), (2, -3), (3, -2), (-2, 3)]
            ]
            move_positions += [Position(x + i, y + j, 1) for i,j in [(1, 1), (1, -1), (-1, -1), (-1, 1)]]
            for pos in move_positions:
                if board.is_empty(pos):
                    moves.append(Move(curr_pos, pos))
                else:
                    target_piece = board.get_piece_at(pos)
                    if target_piece and target_piece.color != self.color:
                        moves.append(Move(curr_pos, pos, is_capture=True))

        elif z == 1:
            move_positions = [Position(x + i, y + j, 1) for i, j in [(1, 1), (1, -1), (-1, -1), (-1, 1)]]
            move_positions += [Position(x + i, y + j, 2) for i, j in [(1, 1), (1, -1), (-1, -1), (-1, 1)]]
            for pos in move_positions:
                if board.is_empty(pos):
                    moves.append(Move(curr_pos, pos))
                else:
                    target_piece = board.get_piece_at(pos)
                    if target_piece and target_piece.color != self.color:
                        moves.append(Move(curr_pos, pos, is_capture=True))
        moves = [move for move in moves if board.is_within_bounds(move.to_position)]
        return moves

    def can_promote(self) -> bool:
        return False
