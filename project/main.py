from contextlib import asynccontextmanager
from fastapi import FastAPI

from .config import settings
from .database import engine
from .routers import router as User

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(User)

@app.get("/")
async def root():
    return {"message": "Hello World"}