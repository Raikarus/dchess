from dependency_injector.wiring import Provide, inject
from app.core import Container


def register_behavior(piece_type: "PieceType"):
    @inject
    def wrapper(cls, piece_behavior_map=Provide[Container.piece_behavior_map]):
        piece_behavior_map.append((cls, piece_type))
        print(piece_behavior_map)
        return cls

    return wrapper
