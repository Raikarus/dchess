from typing import List
from .base import Base
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector, Board


class Mage(Base):
    def __call__(self, position: Position, board: Board) -> List[MovePattern]:
        vectors = []
        max_length = max(board.geometry.width, board.geometry.height)
        if position.z == 1:
            vectors += [Vector(Position(i, j, 0), max_length) for i in range(-1, 2) for j in range(-1, 2) if
                        (i, j) != (0, 0)]
        else:
            vectors += [Vector(Position(i, j, 0), 1) for i in range(-1, 2) for j in range(-1, 2) if
                        (abs(i), abs(j)) in [(1, 0), (0, 1)]]
        vectors += [Vector(Position(0, 0, i), board.geometry.depth) for i in range(-1, 2, 2)]
        move_patterns = [MovePattern(vector, vector) for vector in vectors]
        return move_patterns
