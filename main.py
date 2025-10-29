import fastapi
import uvicorn
from app.core import Container
from app.presentation.api.routers import gameRouter

container = Container()
container.init_resources()

app = fastapi.FastAPI()

app.include_router(gameRouter)

uvicorn.run(app)
