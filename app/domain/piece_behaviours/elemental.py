from typing import List
from .base import Base
from app.domain import Board
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector


class Elemental(Base):
    def __call__(self, position: Position, board: Board) -> List[MovePattern]:
        piece_type, color = board.get_piece_at(position)
        move_patterns = []
        if position.z == 0:
            vectors = [Vector(Position(i, j, 0), 1) for i in range(-2, 3) for j in range(-2, 3) if
                       i == 0 or j == 0 and (i, j) != (0, 0)]
            move_patterns += [MovePattern(vector, vector) for vector in vectors]
            vectors = [Vector(Position(i, j, 0), 1) for i in range(-1, 2) for j in range(-1, 2) if
                       (abs(i), abs(j)) == (1, 1)]
            move_patterns += [MovePattern(vector, Vector(Position(0, 0, 0), 0)) for vector in vectors]
            vectors = [Vector(Position(i, j, 1), 1) for i in range(-1, 2) for j in range(-1, 2) if
                       (abs(i), abs(j)) in [(0, 1), (1, 0)]
                       ]
            move_patterns += [MovePattern(vector, vector, only_in_attack=True) for vector in vectors]
        else:
            vectors = [Vector(Position(i, j, -1), 1) for i in range(-1, 2) for j in range(-1, 2) if
                       i == 0 or j == 0 and (i, j) != (0, 0)]
            move_patterns += [MovePattern(vector, vector) for vector in vectors]

        return move_patterns
