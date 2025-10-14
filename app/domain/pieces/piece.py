from abc import ABC, abstractmethod
from typing import List, Optional, Type, Dict
from ..color import Color
from ..position import Position
from ..move import Move


class Piece(ABC):
    def __init__(self, position: "Position", color: Color, symbol: str = "Unknown", has_moved: bool = False):
        self.position = position
        self.color = color
        self.symbol = symbol
        self.has_moved = has_moved

    @abstractmethod
    def possible_moves(self, board: "Board") -> List["Move"]:
        pass

    def move(self, move: "Move") -> None:
        """
        Обновляет позицию фигуры при выполнении хода
        """
        self.position = move.to_position
        self.has_moved = True

    def can_promote(self) -> bool:
        """
        Проверяет, может ли фигура быть превращена
        """
        return False

    def promote(self, new_piece_type: str) -> Optional["Piece"]:
        """
        Выполняет превращение фигуры в новую по типу, если возможно
        Возвращает новую фигуру или None, если превращение невозможно
        """
        if not self.can_promote():
            return None
        return PieceFactory.create_piece(new_piece_type, self.position, self.color)


class PieceFactory:
    _registry: Dict[str, Type["Piece"]] = {}

    @classmethod
    def register_piece(cls, piece_type: str, piece_class: Type["Piece"]) -> None:
        """
        Зарегистрировать класс фигуры под указанным типом
        """
        cls._registry[piece_type] = piece_class

    @classmethod
    def create_piece(cls, piece_type: str, position: "Position", color: Color, symbol: str, **kwargs) -> Optional["Piece"]:
        piece_class = cls._registry.get(piece_type)
        if not piece_class:
            raise ValueError(f"Unknown piece type: {piece_type}")
        # Создаём новый экземпляр с нужными параметрами
        return piece_class(position=position, color=color, symbol=symbol, **kwargs)


def register_piece(piece_type: str):
    def decorator(cls):
        PieceFactory.register_piece(piece_type, cls)
        return cls
    return decorator
