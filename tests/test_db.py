from dataclasses import asdict

import pytest
from sqlalchemy import select

from project.models import User
from project.security import get_password_hash


@pytest.mark.asyncio
async def test_db_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        password_hash = get_password_hash('senha')
        new_user = User(
            name='alice', email='teste@test', password=password_hash
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.name == 'alice'))

    assert asdict(user) == {
        'created_at': time,
        'updated_at': None,
        'deleted_at': None,
        'is_deleted': False,
        'id': 1,
        'email': 'teste@test',
        'name': 'alice',
        'password': password_hash,
        'frameworks': [],
    }
