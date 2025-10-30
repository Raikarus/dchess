from typing import List
from .base import Base
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector


class Hero(Base):
    def __call__(self, position: Position, *args) -> List[MovePattern]:
        vectors = []

        move_patterns = [MovePattern(vector, vector) for vector in vectors]
        return move_patterns
