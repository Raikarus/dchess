import fastapi
import uvicorn
from app.core.container import Container
from app.presentation.api.routers import gameRouter
from app.domain.aggregates import Game
from app.domain.piece_behaviours import King

container = Container()
container.init_resources()

king = King()
king()

# app = fastapi.FastAPI()
#
# app.include_router(gameRouter)
#
# uvicorn.run(app)
