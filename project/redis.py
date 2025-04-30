from redis import asyncio as redis_asyncio

from project.config import settings


async def get_redis():
    client = redis_asyncio.from_url(settings.REDIS_URL)
    try:
        yield client
    finally:
        await client.close()
