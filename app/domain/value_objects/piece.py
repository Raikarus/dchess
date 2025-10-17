from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Piece:
    type: "PieceType"


class PieceType(Enum):
    KING = 0
    SYLF = 1
    GRYPHON = 2
