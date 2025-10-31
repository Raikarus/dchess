import fastapi
import uvicorn
from app.core import Container
from app.presentation.api.routers import gameRouter

container = Container()
container.init_resources()

app = fastapi.FastAPI()
app.include_router(gameRouter)

container.wire(modules=[__name__])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
