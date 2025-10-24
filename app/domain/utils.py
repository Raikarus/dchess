from app.domain.value_objects import PieceType
from dependency_injector.wiring import Provide, inject
from app.core import Container
from typing import List, Tuple


def register_behavior(piece_type):
    @inject
    def wrapper(cls, piece_behavior_map_provider=Provide[Container.piece_behavior_map]):
        piece_behavior_map = piece_behavior_map_provider()
        piece_behavior_map.append((cls, piece_type))
        return cls

    return wrapper
