from abc import ABC, abstractmethod
from typing import List
from app.domain.move_pattern import MovePattern


class Base(ABC):

    @abstractmethod
    def __call__(self, *args, **kwargs) -> List[MovePattern]:
        """
        :return: Вектора движения фигуры
        """
        pass
