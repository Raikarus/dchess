from dataclasses import dataclass
from typing import Optional
from app.domain.value_objects.position import Position


@dataclass(frozen=True)
class Move:
    from_position: Position
    to_position: Position
    attack_position: Optional[Position] = None
