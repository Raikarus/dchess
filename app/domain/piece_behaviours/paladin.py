from typing import List
from .base import Base
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector


class Paladin(Base):
    def __call__(self, position: Position, *args) -> List[MovePattern]:
        vectors = []
        if position.z == 1:
            vectors += [Vector(Position(i, j, 0), 1) for i in range(-2, 3) for j in range(-2, 3) if
                        (abs(i), abs(j)) in [(2, 1), (1, 2)]]
        vectors += [Vector(Position(i, j, 0), 1) for i in range(-1, 2) for j in range(-1, 2) if (i, j) != (0, 0)]
        vectors += [Vector(Position(i, 0, j), 1) for i in range(-2, 3) for j in range(-2, 3) if
                    (abs(i), abs(j)) in [(2, 1), (1, 2)]]
        vectors += [Vector(Position(0, i, j), 1) for i in range(-2, 3) for j in range(-2, 3) if
                    (abs(i), abs(j)) in [(2, 1), (1, 2)]]
        move_patterns = [MovePattern(vector, vector) for vector in vectors]
        return move_patterns
