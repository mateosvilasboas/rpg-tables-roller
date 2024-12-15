from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database import  Base, engine
from .routers import router as example

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(example)

@app.get("/")
async def root():
    return {"message": "Hello World"}