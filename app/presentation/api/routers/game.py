from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status, Depends
from app.domain.value_objects import Position
from app.core import Container
from app.domain.aggregates.game import Game
from app.domain.value_objects.move import Move
from ..schemas import (
    MoveRequest,
)

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post("/make_move", status_code=status.HTTP_200_OK)
@inject
async def make_move(move: MoveRequest, game_manager: Game = Depends(Provide[Container.game_manager])):
    from_pos = Position(move.from_position.x, move.from_position.y, move.from_position.z)
    to_pos = Position(move.to_position.x, move.to_position.y, move.to_position.z)
    move_obj = Move(from_position=from_pos, to_position=to_pos)

    try:
        game_manager.move_piece(move_obj)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Invalid move: {err}")
    return {"success": True, "message": "Move made successfully"}


@router.get("/state", status_code=status.HTTP_200_OK)
@inject
async def get_state(game_manager: Game = Depends(Provide[Container.game_manager])):
    return {
        "current_turn": game_manager.current_turn.name,
        "game_state": game_manager.state.name,
        "board": str(game_manager.board),
        "move_history": [str(m) for m in game_manager.move_history]
    }


@router.post("/new", status_code=status.HTTP_200_OK)
@inject
async def reset_game(game_manager: Game = Depends(Provide[Container.game_manager])):
    try:
        game_manager.reset()
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Reset failed: {err}")
    return {"message": "Game reset successfully"}


@router.get("/moves", status_code=status.HTTP_200_OK)
@inject
async def get_available_moves(game_manager: Game = Depends(Provide[Container.game_manager])):
    moves = game_manager.get_all_possible_moves()
    # Конвертация доменных объектов Move в Pydantic Move
    result = []
    for m in moves:
        move_data = {
            "from_position": {"x": m.from_position.x, "y": m.from_position.y, "z": m.from_position.z},
            "to_position": {"x": m.to_position.x, "y": m.to_position.y, "z": m.to_position.z},
            "attack_position": None if m.attack_position is None else {
                "x": m.attack_position.x, "y": m.attack_position.y, "z": m.attack_position.z
            }
        }
        result.append(Move(**move_data))
    return result


@router.post("/undo", status_code=status.HTTP_200_OK)
@inject
async def undo_move(game_manager: Game = Depends(Provide[Container.game_manager])):
    try:
        game_manager.undo_move()
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Can't undo move: {err}")
    return {"message": "Последний ход отменён"}
