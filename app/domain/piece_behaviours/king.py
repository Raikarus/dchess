from typing import List
from .base import Base
from app.domain.value_objects import Position, Move, PieceType
from app.domain import Board, MovePattern, Vector


class King(Base):
    def __call__(self, position: Position) -> List["MovePattern"]:
        vectors = [Vector(Position(0, 0, 1), 1), Vector(Position(0, 0, -1), 1)]
        if position.z == 1:
            vectors += [Vector(Position(i, j, 0), 1) for i in range(-1, 2) for j in range(-1, 2) if (i, j) != (0, 0)]

        move_patterns = [MovePattern(vector, vector) for vector in vectors]
        return move_patterns
