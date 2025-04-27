from fastapi import FastAPI

from .routers.auth import router as Auth
from .routers.frameworks import router as Framework
from .routers.users import router as User

app = FastAPI()

app.include_router(User)
app.include_router(Auth)
app.include_router(Framework)


@app.get('/')
async def root():
    return {'message': 'Hello World'}
