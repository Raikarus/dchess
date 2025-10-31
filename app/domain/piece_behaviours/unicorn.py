from typing import List
from .base import Base
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector


class Unicorn(Base):
    def __call__(self, position: Position, *args) -> List[MovePattern]:
        vectors = []
        vectors += [Vector(Position(i, j, 0), 1) for i in range(-2, 3) for j in range(-2, 3) if
                    (abs(i), abs(j)) in [(2, 1), (1, 2)]]
        move_patterns = [MovePattern(vector, vector) for vector in vectors]
        return move_patterns
