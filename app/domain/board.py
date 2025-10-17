from typing import Optional, List, Tuple, Dict
from .move import Move
from .position import Position
from .color import Color
from app.domain.value_objects.board_geometry import BoardGeometry
from dataclasses import dataclass, field


@dataclass
class Board:
    id: int
    geometry: BoardGeometry = BoardGeometry(width=8, height=12, depth=3)
    start_positions: Dict[Tuple[str, Color], List[Position]] = field(default_factory=Dict)
    pieces: Dict[Position, "Piece"] = field(default_factory=Dict)

    def is_within_bounds(self, position: Position) -> bool:
        return (0 <= position.x < self.width and
                0 <= position.y < self.height and
                0 <= position.z < self.depth)

    def register_start_positions(self, piece: str, color: Color, positions: List[Position]) -> None:
        """
        Зарегистрировать стартовые позиции для фигур (ТИП ФИГУРЫ ПЕРЕДАВАТЬ СТРОКОЙ С МАЛЕНЬКОЙ БУКВЫ)
        """
        key = (piece, color)
        self._start_positions[key] = positions

    def get_start_positions_for_piece(self, piece: str, color: Color) -> List[Position]:
        """
        Вернуть стартовые позиции для фигуры данного типа (ТИП ФИГУРЫ ПЕРЕДАВАТЬ СТРОКОЙ С МАЛЕНЬКОЙ БУКВЫ)
        """
        key = (piece, color)
        return self._start_positions.get(key, [])

    def get_piece_at(self, position: Position) -> Optional["Piece"]:
        return self._pieces.get(position)

    def is_empty(self, position: Position) -> bool:
        return position not in self._pieces

    def place_piece(self, piece: "Piece") -> None:
        self._pieces[piece.position] = piece

    def move_piece(self, move: Move) -> None:
        piece = self._pieces.pop(move.from_position)
        piece.position = move.to_position
        self._pieces[move.to_position] = piece
