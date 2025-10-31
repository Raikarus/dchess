from dependency_injector import containers, providers
from app.domain.aggregates import Game
from app.domain.value_objects import PieceType
from app.domain.piece_behaviours import *


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
        PieceType.DRAGON: providers.Singleton(Dragon),
        PieceType.WARRIOR: providers.Singleton(Warrior),
        PieceType.HERO: providers.Singleton(Hero),
        PieceType.OLIPHANT: providers.Singleton(Oliphant),
        PieceType.UNICORN: providers.Singleton(Unicorn),
        PieceType.THIEF: providers.Singleton(Thief),
        PieceType.CLERIC: providers.Singleton(Cleric),
        PieceType.MAGE: providers.Singleton(Mage),
        PieceType.PALADIN: providers.Singleton(Paladin),
        PieceType.DWARF: providers.Singleton(Dwarf),
        PieceType.BASILISK: providers.Singleton(Basilisk),
        PieceType.ELEMENTAL: providers.Singleton(Elemental)
    })
    game_manager = providers.Singleton(Game, players=["White Player", "Black Player"],
                                       piece_behaviour_map=piece_behaviour_map)
