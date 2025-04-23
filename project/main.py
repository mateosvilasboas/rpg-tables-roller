from fastapi import FastAPI

from .routers import router as User

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with engine.begin():
#         yield
#     await engine.dispose()


app = FastAPI()

app.include_router(User)


@app.get('/')
async def root():
    return {'message': 'Hello World'}
