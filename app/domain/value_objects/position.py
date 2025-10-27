from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: int
    y: int
    z: int

    def __mul__(self, other):
        if isinstance(other, int):
            return Position(self.x * other, self.y * other, self.z * other)
        return NotImplemented

    def __rmul__(self, other):
        # для поддержки умножения с другой стороны
        return self.__mul__(other)

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented
