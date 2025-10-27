import fastapi
import uvicorn
from app.domain.aggregates import Game
from app.core import Container
from app.presentation.api.routers import gameRouter
from app.domain.value_objects import Position

container = Container()
container.init_resources()

game = Game(["p1", "p2"])
king = game.board.get_piece_at(Position(6, 0, 1))
print(container.piece_behaviour_map)
print(f"King is {king}")
# app = fastapi.FastAPI()
#
# app.include_router(gameRouter)
#
# uvicorn.run(app)
