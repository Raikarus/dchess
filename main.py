import fastapi
import uvicorn
from app.domain.aggregates import Game
from app.core import Container
from app.presentation.api.routers import gameRouter
from app.domain.value_objects import Position
from app.domain.services import GetStrategy

container = Container()
container.init_resources()
game = Game(["p1", "p2"])
strategy_service = GetStrategy(game)
piece_position = Position(6, 0, 1)
piece = game.board.get_piece_at(piece_position)
print(f"Piece is {piece}")
print(strategy_service.get_strategy(piece_position))
# app = fastapi.FastAPI()
#
# app.include_router(gameRouter)
#
# uvicorn.run(app)
