from dataclasses import dataclass
from app.domain.value_objects import Position

@dataclass(frozen=True)
class Vector:
    dPos: Position
    length: int
