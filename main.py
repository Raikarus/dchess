import fastapi
import uvicorn
from app.core.container import Container
from app.presentation.api.routers import gameRouter
from app.domain.aggregates import Game

container = Container()
container.init_resources()

app = fastapi.FastAPI()

app.include_router(gameRouter)

uvicorn.run(app)
