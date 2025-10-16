from fastapi import APIRouter, HTTPException
from app.domain.position import Position
from app.domain.move import Move
from app.domain.game_manager import GameManager, GameState
from ..schemas import (
    MoveResponse,
    MoveRequest
)

router = APIRouter()


# Создаем сессию игры
game_manager = GameManager(players=["White Player", "Black Player"])


@router.post("/make_move", response_model=MoveResponse)
async def make_move(move: MoveRequest):
    from_pos = Position(move.from_x, move.from_y, move.from_z)
    to_pos = Position(move.to_x, move.to_y, move.to_z)
    move_obj = Move(from_position=from_pos, to_position=to_pos)

    success = game_manager.make_move(move_obj)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid move")
    return MoveResponse(success=True, message="Move made successfully")


@router.get("/state")
async def get_state():
    return {
        "current_turn": game_manager.current_turn.name,
        "game_state": game_manager.state.name,
        "board": str(game_manager.board),
        "move_history": [str(m) for m in game_manager.move_history]
    }
