import asyncio
from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from factories import FrameworkFactory, UserFactory
from fastapi.testclient import TestClient
from redis import asyncio as redis_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from project.database import get_db
from project.main import app
from project.models import Base
from project.redis import get_redis
from project.security.auth import get_password_hash


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


@pytest.fixture
def client(db_session, redis_session):
    def get_db_override():
        return db_session

    def get_redis_override():
        return redis_session

    with TestClient(app) as client:
        app.dependency_overrides[get_db] = get_db_override
        app.dependency_overrides[get_redis] = get_redis_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def postgres_engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest.fixture(scope='session')
def redis_engine(event_loop):
    with RedisContainer('redis:7-alpine') as redis:
        _engine = redis_asyncio.from_url(
            f"""redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(6379)}"""
        )
        yield _engine


@pytest_asyncio.fixture
async def db_session(postgres_engine):
    async with postgres_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(
        postgres_engine, expire_on_commit=False
    ) as session:
        yield session

    async with postgres_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def redis_session(redis_engine):
    try:
        await redis_engine.flushall()
        yield redis_engine
    finally:
        try:
            await redis_engine.flushall()
        except RuntimeError:
            # Ignore erros se o event loop já estiver fechado
            pass


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture(autouse=True)
def mock_redis_denylist(monkeypatch):
    denied_tokens = {}

    async def mock_exists(self, key):
        result = False
        if key in denied_tokens:
            result = True
        return result

    async def mock_set(self, key, value, **kwargs):
        denied_tokens[key] = value
        return True

    monkeypatch.setattr(redis_asyncio.Redis, 'exists', mock_exists)
    monkeypatch.setattr(redis_asyncio.Redis, 'set', mock_set)


@pytest_asyncio.fixture
async def user(db_session):
    password = 'senha1'
    hashed_password = get_password_hash(password)
    user = UserFactory(password=hashed_password)

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    user.frameworks = []
    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def other_user(db_session):
    password = 'senha2'
    hashed_password = get_password_hash(password)
    user = UserFactory(password=hashed_password)

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    user.frameworks = []
    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def framework(db_session, user):
    framework = FrameworkFactory(user_id=user.id)

    framework.entries = {
        'entry_key_1': 'entry_value_1',
        'entry_key_2': 'entry_value_2',
        'entry_key_3': 'entry_value_3',
        'entry_key_4': 'entry_value_4',
    }

    db_session.add(framework)
    await db_session.commit()
    await db_session.refresh(framework)

    return framework


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']
