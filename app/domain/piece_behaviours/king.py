from typing import List
from app.domain.value_objects.piece import Piece, register_piece
from ..position import Position
from ..move import Move


@register_piece("king")
class King(Piece):

    def possible_moves(self, board: "Board") -> List["Move"]:
        moves = []
        curr_pos = self.position
        x, y, z = curr_pos.x, curr_pos.y, curr_pos.z

        if z == 1:
            move_positions = [
                Position(x + i, y + j, 1) for i, j in [(0, 1), (1, 1), (1, 0), (1, -1),
                                                       (0, -1), (-1, -1), (-1, 0), (-1, 1)]
            ]
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
