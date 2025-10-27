from dependency_injector.wiring import Provide, inject
from app.core import Container


class GetStrategy:
    @inject
    def __init__(self, piece_behavior_map: dict = Provide[Container.piece_behaviour_map]):
        self.piece_behavior_map = piece_behavior_map

    def get_strategy(self, piece_type: "PieceType"):
        strategy_provider = self.piece_behavior_map.get(piece_type)
        if not strategy_provider:
            raise ValueError(f"No strategy for {piece_type}")
        return strategy_provider()  # создается или берется синглтон
