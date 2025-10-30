from typing import Optional, List, Tuple, Dict
from .color import Color
from .value_objects import PieceType, BoardGeometry, Position, Move
from dataclasses import dataclass, field


@dataclass
class Board:
    geometry: BoardGeometry = BoardGeometry(width=8, height=12, depth=3)
    start_positions: Dict[Tuple["PieceType", Color], List[Position]] = field(default_factory=dict)
    pieces: Dict[Position, Tuple["PieceType", Color]] = field(default_factory=dict)

    def is_within_bounds(self, position: Position) -> bool:
        return (0 <= position.x < self.geometry.width and
                0 <= position.y < self.geometry.height and
                0 <= position.z < self.geometry.depth)

    def get_piece_at(self, position: Position) -> Optional[Tuple["PieceType", Color]]:
        return self.pieces.get(position)

    def is_empty(self, position: Position) -> bool:
        return position not in self.pieces

    def place_piece(self, piece_type: "PieceType", color: Color, position: Position) -> None:
        self.pieces[position] = (piece_type, color)

    def move_piece(self, move: Move) -> Optional[Tuple[PieceType, Color]]:
        if not self.is_within_bounds(move.from_position) or not self.is_within_bounds(move.to_position):
            raise ValueError("Move positions out of board bounds")

        moving_piece = self.get_piece_at(move.from_position)
        if moving_piece is None:
            raise ValueError(f"No piece at source position {move.from_position}")

        target_piece = self.get_piece_at(move.to_position)

        # Удаляем фигуру с начальной позиции
        self.pieces.pop(move.from_position)

        # Если была фигура на позиции назначения — она берётся (удаляется)
        captured_piece = None
        if target_piece is not None and target_piece[1] != moving_piece[1]:
            captured_piece = target_piece
            self.pieces.pop(move.to_position)

        # Ставим фигуру на новую позицию
        self.pieces[move.to_position] = moving_piece

        return captured_piece
