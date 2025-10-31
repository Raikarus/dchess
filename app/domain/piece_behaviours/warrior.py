from typing import List, Optional
from .base import Base
from app.domain import Board
from app.domain.value_objects import Position, PieceType
from app.domain import MovePattern, Vector, Color


class Warrior(Base):
    def __call__(self, position: Position, board: Board) -> List[MovePattern]:
        piece_type, color = board.get_piece_at(position)
        vectors = []
        forward = 1 if color == Color.WHITE else -1
        move_patterns = []
        if position.z == 1:
            vectors = [Vector(Position(1, forward, 0), 1), Vector(Position(-1, forward, 0), 1)]
            move_patterns = [MovePattern(vector, vector, only_in_attack=True) for vector in vectors]
            vectors = [Vector(Position(0, 0, -1), 1), Vector(Position(0, forward, 0), 1)]
            move_patterns += [MovePattern(vector, Vector(Position(0, 0, 0), 0)) for vector in vectors]
        return move_patterns

    def is_promote(self, board: Board, position: Position) -> bool:
        piece_type, color = board.get_piece_at(position)
        return (position.y == (board.geometry.height - 1) and color == Color.WHITE) or (
                    position.y == 0 and color == color.BLACK)

    def get_promote_type(self) -> Optional["PieceType"]:
        return PieceType.HERO
