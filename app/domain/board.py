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
        return (0 <= position.x < self.geometry.width and
                0 <= position.y < self.geometry.height and
                0 <= position.z < self.geometry.depth)

    def get_piece_at(self, position: Position) -> Optional["Piece"]:
        return self.pieces.get(position)

    def is_empty(self, position: Position) -> bool:
        return position not in self.pieces

    def place_piece(self, piece: "Piece") -> None:
        self.pieces[piece.position] = piece

    def move_piece(self, move: Move) -> None:
        piece = self.pieces.pop(move.from_position)
        piece.position = move.to_position
        self.pieces[move.to_position] = piece
