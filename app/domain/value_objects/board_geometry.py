from dataclasses import dataclass


@dataclass(frozen=True)
class BoardGeometry:
    width: int
    height: int
    depth: int
