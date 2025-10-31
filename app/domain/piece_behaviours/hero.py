from typing import List
from .base import Base
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector


class Hero(Base):
    def __call__(self, position: Position, *args) -> List[MovePattern]:
        vectors = []
        if position.z != 1:
            vectors += [Vector(Position(i, j, -1 if position.z == 2 else 1), 1) for i in range(-1, 2) for j in
                        range(-1, 2) if
                        (abs(i), abs(j)) == (1, 1)]
        else:
            vectors += [Vector(Position(i, j, k), 1) for i in range(-1, 2) for j in
                        range(-1, 2) for k in range(-1, 2) if
                        (abs(i), abs(j), abs(k)) == (1, 1, 1)]
            vectors += [Vector(Position(i, j, 0), 1) for i in range(-1, 2) for j in range(-1, 2) if
                        (abs(i), abs(j)) == (1, 1)]
            vectors += [Vector(Position(i, j, 0), 1) for i in range(-2, 3) for j in range(-2, 3) if
                        (abs(i), abs(j)) == (2, 2)]
        move_patterns = [MovePattern(vector, vector) for vector in vectors]
        return move_patterns
