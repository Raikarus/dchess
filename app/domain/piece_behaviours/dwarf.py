from typing import List, Optional
from .base import Base
from app.domain import Board
from app.domain.value_objects import Position, PieceType
from app.domain import MovePattern, Vector, Color


class Dwarf(Base):
    def __call__(self, position: Position, board: Board) -> List[MovePattern]:
        piece_type, color = board.get_piece_at(position)
        forward = 1 if color == Color.WHITE else -1
        move_patterns = []
        attack_vectors = [Vector(Position(1, forward, 0), 1), Vector(Position(-1, forward, 0), 1)]
        move_vectors = [Vector(Position(0, forward, 0), 1), Vector(Position(-1, 0, 0), 1), Vector(Position(1, 0, 0), 1)]
        if position.z == 0:
            attack_vectors += [Vector(Position(0, 0, 1), 1)]
        else:
            move_vectors += [Vector(Position(0, 0, -1), 1)]
        move_patterns += [MovePattern(vector, Vector(Position(0, 0, 0), 0)) for vector in move_vectors]
        move_patterns += [MovePattern(vector, vector, only_in_attack=True) for vector in attack_vectors]
        return move_patterns
