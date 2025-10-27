from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.move_pattern import MovePattern


class Base(ABC):

    @abstractmethod
    def __call__(self, *args, **kwargs) -> List[MovePattern]:
        """
        :return: Вектора движения фигуры
        """
        pass

    def is_promote(self, positions: List["Position"]) -> bool:
        return False

    def get_promote_type(self) -> Optional["PieceType"]:
        return None
