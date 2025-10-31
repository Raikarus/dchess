from typing import List
from .base import Base
from app.domain import Board
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector


class Oliphant(Base):
    def __call__(self, position: Position, board: Board) -> List[MovePattern]:
        move_patterns = []
        max_length = max(board.geometry.width, board.geometry.height)
        vectors = [Vector(Position(i, j, 0), max_length) for i in range(-1, 2) for j in range(-1, 2) if
                   (abs(i), abs(j)) in [(1, 0), (0, 1)]]
        move_patterns += [MovePattern(vector, vector) for vector in vectors]
        return move_patterns
