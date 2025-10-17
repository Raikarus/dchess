from dependency_injector import containers, providers
from app.domain.aggregates.game_manager import GameManager
from typing import List, Tuple


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.presentation.api"
        ]
    )
    config = providers.Configuration()

    game_manager = providers.Singleton(GameManager, players=["White Player", "Black Player"])
    piece_behavior_map = providers.Object(List[Tuple["PieceBehaviour", "PieceType"]])
