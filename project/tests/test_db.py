from dataclasses import asdict

import pytest
from sqlalchemy import select

from project.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(name='alice', email='teste@test')
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.name == 'alice'))

    assert asdict(user) == {
        'id': 1,
        'name': 'alice',
        'email': 'teste@test',
        'created_at': time,
    }
