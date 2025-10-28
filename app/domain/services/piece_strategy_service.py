from dependency_injector.wiring import Provide, inject
from app.core import Container
from app.domain.value_objects import Move
from typing import List


class PieceStrategyService:
    @inject
    def __init__(self, game: "Game", piece_behavior_map: dict = Provide[Container.piece_behaviour_map]):
        self.piece_behavior_map = piece_behavior_map
        self.board = game.board

    def get_strategy(self, piece_position: "Position") -> List[Move]:
        piece_type, piece_color = self.board.get_piece_at(piece_position)
        strategy_provider = self.piece_behavior_map.get(piece_type)
        if not strategy_provider:
            raise ValueError(f"No strategy for {piece_type}")
        move_patterns = strategy_provider(piece_position)  # создается или берется синглтон
        possible_moves = []
        for move_pattern in move_patterns:
            for i in range(move_pattern.move_vector.length):
                new_piece_position = piece_position + move_pattern.move_vector.dPos * (i + 1)
                if not self.board.is_empty(new_piece_position):
                    target_piece_type, target_piece_color = self.board.get_piece_at(new_piece_position)
                else:
                    target_piece_type, target_piece_color = None, None
                if self.board.is_within_bounds(new_piece_position) and target_piece_color != piece_color:
                    is_capture = target_piece_color is not None
                    promote_type = strategy_provider.get_promote_type()
                    possible_moves += [Move(piece_position, new_piece_position, is_capture, promote_type)]
        return possible_moves
