from fastapi import FastAPI

from .routers.users import router as User

app = FastAPI()

app.include_router(User)


@app.get('/')
async def root():
    return {'message': 'Hello World'}
