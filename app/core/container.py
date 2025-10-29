from dependency_injector import containers, providers
from app.domain.aggregates import Game
from app.domain.value_objects import PieceType
from app.domain.piece_behaviours import (King, Sylph, Gryphon)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.presentation.api"
        ]
    )
    config = providers.Configuration()
    piece_behaviour_map = providers.Dict({
        PieceType.KING: providers.Singleton(King),
        PieceType.SYLPH: providers.Singleton(Sylph),
        PieceType.GRYPHON: providers.Singleton(Gryphon),
    })
    game_manager = providers.Singleton(Game, players=["White Player", "Black Player"],
                                       piece_behaviour_map=piece_behaviour_map)
