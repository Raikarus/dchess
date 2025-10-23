from dataclasses import dataclass
from typing import Optional
from app.domain.value_objects.position import Position


@dataclass
class Move:
    from_position: Position
    to_position: Position
    is_capture: bool = False
    promotion_piece_type: Optional[str] = None
