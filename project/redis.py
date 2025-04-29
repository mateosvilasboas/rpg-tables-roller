from redis import asyncio as redis_asyncio

from .config import settings

Redis = redis_asyncio.from_url(settings.REDIS_URL)


async def get_redis():
    async with Redis() as redis:
        try:
            yield redis
        finally:
            await redis.close()
