import fastapi
import uvicorn
from app.presentation.api.routers import gameRouter
app = fastapi.FastAPI()
app.include_router(gameRouter, prefix="/api/game", tags=["game"])
uvicorn.run(app)
