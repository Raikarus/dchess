from typing import List
from .base import Base
from app.domain import Board
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector, Color


class Basilisk(Base):
    def __call__(self, position: Position, board: Board) -> List[MovePattern]:
        piece_type, color = board.get_piece_at(position)
        forward = 1 if color == Color.WHITE else -1
        backward = forward * (-1)
        move_patterns = []
        vectors = [Vector(Position(i, forward, 0), 1) for i in range(-1, 2)]
        move_patterns += [MovePattern(vector, vector) for vector in vectors]
        move_patterns += [MovePattern(Vector(Position(0, backward, 0), 1), Vector(Position(0, 0, 0), 0))]
        return move_patterns
