from fastapi import APIRouter, HTTPException, status, Depends
from app.domain.value_objects.position import Position
from app.domain.value_objects.move import Move
from app.domain.aggregates.game import Game
from ..schemas import (
    MoveResponse,
    MoveRequest
)
from dependency_injector.wiring import Provide, inject
from app.core import Container

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post("/make_move", response_model=MoveResponse, status_code=status.HTTP_200_OK)
@inject
async def make_move(move: MoveRequest, game_manager: Game = Depends(Provide[Container.game_manager])):
    from_pos = Position(move.from_x, move.from_y, move.from_z)
    to_pos = Position(move.to_x, move.to_y, move.to_z)
    move_obj = Move(from_position=from_pos, to_position=to_pos)

    success = game_manager.make_move(move_obj)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid move")
    return MoveResponse(success=True, message="Move made successfully")


@router.get("/state", status_code=status.HTTP_200_OK)
@inject
async def get_state(game_manager: Game = Depends(Provide[Container.game_manager])):
    return {
        "current_turn": game_manager.current_turn.name,
        "game_state": game_manager.state.name,
        "board": str(game_manager.board),
        "move_history": [str(m) for m in game_manager.move_history]
    }
