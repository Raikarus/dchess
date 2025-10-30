from typing import List
from .base import Base
from app.domain import Board
from app.domain.value_objects import Position
from app.domain import MovePattern, Vector


class Sylph(Base):

    def __call__(self, position: Position, board: Board) -> List[MovePattern]:
        piece_type, color = board.get_piece_at(position)
        vectors = []
        forward = 1 if color == color.WHITE else -1
        move_patterns = []
        if position.z == 2:
            vectors += [Vector(Position(0, 0, -1), 1), Vector(Position(0, forward, 0), 1)]
            move_patterns = [MovePattern(vector, vector, only_in_attack=True) for vector in vectors]
            vectors = [Vector(Position(1, 1, 0), 1), Vector(Position(-1, 1, 0), 1)]
            move_patterns += [MovePattern(vector, Vector(Position(0, 0, 0), 0)) for vector in vectors]
        elif position.z == 1:
            start_positions = board.start_positions[(piece_type, color)]
            vectors += [Vector(Position(start_position.x - position.x, start_position.y - position.y, 1), 1) for
                        start_position in start_positions]
            move_patterns = [MovePattern(vector, Vector(Position(0, 0, 0), 0)) for vector in
                             vectors]
        return move_patterns
