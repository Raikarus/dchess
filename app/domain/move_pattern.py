from dataclasses import dataclass
from app.domain import Vector


@dataclass(frozen=True)
class MovePattern:
    move_vector: Vector
    attack_vector: Vector
