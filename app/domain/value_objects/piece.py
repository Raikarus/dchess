from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Piece:
    type: "PieceType"


class PieceType(Enum):
    KING = 0
    SYLPH = 1
    GRYPHON = 2
    DRAGON = 3
    WARRIOR = 4
    HERO = 5
    OLIPHANT = 6
    UNICORN = 7
    THIEF = 8
    CLERIC = 9
    MAGE = 10
    PALADIN = 11
    DWARF = 12
    BASILISK = 13
