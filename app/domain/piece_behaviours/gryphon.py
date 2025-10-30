from typing import List
from .base import Base
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector


class Gryphon(Base):
    def __call__(self, position: Position, *args) -> List[MovePattern]:
        vectors = []
        if position.z == 1:
            vectors += [Vector(Position(i, j, 0), 1) for i in range(-1, 2) for j in range(-1, 2) if
                        (abs(i), abs(j)) == (1, 1)]
            vectors += [Vector(Position(i, j, 1), 1) for i in range(-1, 2) for j in range(-1, 2) if
                        (abs(i), abs(j)) == (1, 1)]
        if position.z == 2:
            vectors += [Vector(Position(i, j, -1), 1) for i in range(-1, 2) for j in range(-1, 2) if
                        (abs(i), abs(j)) == (1, 1)]
            vectors += [Vector(Position(i, j, 0), 1) for i in range(-3, 4) for j in range(-3, 4) if
                        (abs(i), abs(j)) in [(3, 2), (2, 3)]]

        move_patterns = [MovePattern(vector, vector) for vector in vectors]
        return move_patterns
