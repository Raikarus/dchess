from typing import List
from .base import Base
from app.domain.utils import register_behavior
from app.domain.value_objects import Position, Move, PieceType
from app.domain import Board, MovePattern, Vector


@register_behavior(PieceType.KING)
class King(Base):
    def __call__(self, z: int) -> List["MovePattern"]:
        move_patterns = []

        if z == 1:
            vectors = [Vector(Position(i, j, 1), 1) for i in range(-1, 2) for j in range(-1, 2) if i != j != 0]
            print(vectors)
            return 1
            for pos in move_positions:
                if board.is_empty(pos):
                    moves.append(Move(curr_pos, pos))
                else:
                    target_piece = board.get_piece_at(pos)
                    if target_piece and target_piece.color != self.color:
                        moves.append(Move(curr_pos, pos, is_capture=True))

        moves = [move for move in moves if board.is_within_bounds(move.to_position)]
        return move_patterns
