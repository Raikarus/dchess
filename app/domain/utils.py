from dependency_injector.wiring import Provide, inject
from app.core import Container


def register_behavior(piece_type: "PieceType"):
    @inject
    def wrapper(cls, piece_behaviour_map: dict = Provide[Container.piece_behaviour_map]):
        piece_behaviour_map[piece_type] = cls
        return cls

    return wrapper
