from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Piece:
    type: "PieceType"


class PieceType(Enum):
    KING = 0
    SYLPH = 1
    GRYPHON = 2
