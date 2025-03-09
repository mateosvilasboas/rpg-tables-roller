from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from project.config import settings

engine = create_async_engine(settings.DB_URL, echo=True)
SessionLocal = async_sessionmaker(engine)

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()