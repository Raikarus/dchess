from typing import Callable

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status, Depends, Path

from app.core import Container
from app.domain.aggregates.game import Game
from app.domain.value_objects import Position
from app.domain.value_objects.move import Move
from ..schemas import (
    MoveRequest,
)

router = APIRouter(prefix="/api/game", tags=["game"])


def get_game_by_uuid(game_uuid: str, game_repository) -> "Game":
    game = game_repository.get(game_uuid)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("/{game_uuid}/make_move", status_code=status.HTTP_200_OK)
@inject
async def make_move(
        game_uuid: str = Path(...),
        move: MoveRequest = None,
        game_repository=Depends(Provide[Container.game_repository])
):
    game = get_game_by_uuid(game_uuid, game_repository)
    from_pos = Position(move.from_position.x, move.from_position.y, move.from_position.z)
    to_pos = Position(move.to_position.x, move.to_position.y, move.to_position.z)
    move_obj = Move(from_position=from_pos, to_position=to_pos)

    try:
        game.move_piece(move_obj)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Invalid move: {err}")
    return {"success": True, "message": "Move made successfully"}


def serialize_position(pos):
    return {'x': pos.x, 'y': pos.y, 'z': pos.z}


def serialize_board(board):
    pieces_serialized = {}
    for pos, (ptype, color) in board.pieces.items():
        # Координаты позиции как строка ключ
        key = f"{pos.x}_{pos.y}_{pos.z}"
        pieces_serialized[key] = {
            "piece_type": ptype.name,
            "color": color.name,
            "position": serialize_position(pos)
        }
    return {
        "width": board.geometry.width,
        "height": board.geometry.height,
        "depth": board.geometry.depth,
        "pieces": pieces_serialized
    }


@router.get("/{game_uuid}/state", status_code=status.HTTP_200_OK)
@inject
async def get_state(
        game_uuid: str = Path(...),
        game_repository=Depends(Provide[Container.game_repository])
):
    game = get_game_by_uuid(game_uuid, game_repository)
    return {
        "uuid": str(game.uuid),
        "current_turn": game.current_turn.name,
        "game_state": game.state.name,
        "board": str(game.board),
        "board_obj": serialize_board(game.board),
        "move_history": [str(m) for m in game.move_history],
    }


@router.post("/new", status_code=status.HTTP_201_CREATED)
@inject
async def create_new_game(
        game_factory: Callable = Depends(Provide[Container.game_factory.provider]),
        game_repository=Depends(Provide[Container.game_repository])
):
    new_game = game_factory()

    game_repository.add(new_game)

    return {"message": "New game created", "game_uuid": str(new_game.uuid)}


@router.post("/{game_uuid}/reset", status_code=status.HTTP_200_OK)
@inject
async def reset_game(
        game_uuid: str = Path(...),
        game_repository=Depends(Provide[Container.game_repository])
):
    game = get_game_by_uuid(game_uuid, game_repository)
    try:
        game.reset()
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Reset failed: {err}")
    return {"message": "Game reset successfully"}


@router.get("/{game_uuid}/moves", status_code=status.HTTP_200_OK)
@inject
async def get_available_moves(
        game_uuid: str = Path(...),
        game_repository=Depends(Provide[Container.game_repository])
):
    game = get_game_by_uuid(game_uuid, game_repository)
    moves = game.get_all_possible_moves()
    result = []
    for m in moves:
        move_data = {
            "from_position": {"x": m.from_position.x, "y": m.from_position.y, "z": m.from_position.z},
            "to_position": {"x": m.to_position.x, "y": m.to_position.y, "z": m.to_position.z},
            "attack_position": None if m.attack_position is None else {
                "x": m.attack_position.x,
                "y": m.attack_position.y,
                "z": m.attack_position.z,
            },
        }
        result.append(Move(**move_data))
    return result


@router.post("/{game_uuid}/undo", status_code=status.HTTP_200_OK)
@inject
async def undo_move(
        game_uuid: str = Path(...),
        game_repository=Depends(Provide[Container.game_repository])
):
    game = get_game_by_uuid(game_uuid, game_repository)
    try:
        game.undo_move()
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Can't undo move: {err}")
    return {"message": "Последний ход отменён"}
