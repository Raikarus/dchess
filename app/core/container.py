from dependency_injector import containers, providers
from app.domain.aggregates import Game


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.presentation.api",
            "app.domain.services"
        ],
        modules=[
            "app.domain.utils"
        ]
    )
    config = providers.Configuration()

    game_manager = providers.Singleton(Game, players=["White Player", "Black Player"])
    piece_behaviour_map = providers.Dict({})
