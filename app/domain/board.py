from typing import Optional, List, Tuple, Dict
from .color import Color
from .value_objects import PieceType, BoardGeometry, Position, Move
from dataclasses import dataclass, field


@dataclass
class Board:
    geometry: BoardGeometry = BoardGeometry(width=8, height=12, depth=3)
    start_positions: Dict[Tuple["PieceType", Color], List[Position]] = field(default_factory=dict)
    pieces: Dict[Position, Tuple["PieceType", Color]] = field(default_factory=dict)

    def __str__(self):
        board_str = ""
        for z in range(self.geometry.depth):
            for y in range(self.geometry.height):
                for x in range(self.geometry.width):
                    piece = self.get_piece_at(Position(x, y, z))
                    if piece:
                        board_str += "○"
                    else:
                        board_str += "•"
                board_str += "\n"
            board_str += "-------------------------------\n"
        return board_str

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
