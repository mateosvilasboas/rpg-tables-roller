from fastapi import FastAPI

from project.routers.auth import router as Auth
from project.routers.frameworks import router as Framework
from project.routers.users import router as User

app = FastAPI()

app.include_router(User)
app.include_router(Auth)
app.include_router(Framework)


@app.get('/')
async def root():
    return {'message': 'Hello World'}
