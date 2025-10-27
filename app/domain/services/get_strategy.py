from dependency_injector.wiring import Provide, inject
from app.core import Container


class GetStrategy:
    @inject
    def __init__(self, game: "Game", piece_behavior_map: dict = Provide[Container.piece_behaviour_map]):
        self.piece_behavior_map = piece_behavior_map
        self.board = game.board

    def get_strategy(self, piece_type: "PieceType", piece_position: "Position"):
        strategy_provider = self.piece_behavior_map.get(piece_type)
        if not strategy_provider:
            raise ValueError(f"No strategy for {piece_type}")
        move_patterns = strategy_provider(piece_position)  # создается или берется синглтон
        for move_pattern in move_patterns:
            print(move_pattern.move_vector)
        possible_moves = [123]
        return possible_moves
