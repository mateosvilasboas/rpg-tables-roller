from dataclasses import asdict

import pytest
from sqlalchemy import select

from project.models import Framework, User
from project.security.auth import get_password_hash


@pytest.mark.asyncio
async def test_db_create_user(db_session, mock_db_time):
    with mock_db_time(model=User) as time:
        password_hash = get_password_hash('senha')
        new_user = User(
            name='alice', email='teste@test', password=password_hash
        )
        db_session.add(new_user)
        await db_session.commit()

    user = await db_session.scalar(select(User).where(User.name == 'alice'))

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


@pytest.mark.asyncio
async def test_db_create_framework(db_session, mock_db_time, user: User):
    with mock_db_time(model=Framework) as time:
        new_framework = Framework(
            name='framework',
            user_id=user.id,
        )

        new_framework.entries = {
            'key_1': 'value 1',
            'key_2': 'value 2',
            'key_3': 'value 3',
            'key_4': 'value 4',
        }

        db_session.add(new_framework)
        await db_session.commit()

    framework = await db_session.scalar(
        select(Framework).where(Framework.id == 1)
    )

    assert asdict(framework) == {
        'created_at': time,
        'updated_at': None,
        'deleted_at': None,
        'is_deleted': False,
        'id': 1,
        'name': 'framework',
        'user_id': user.id,
        'entries': {
            'key_1': 'value 1',
            'key_2': 'value 2',
            'key_3': 'value 3',
            'key_4': 'value 4',
        },
    }


@pytest.mark.asyncio
async def test_db_framework_relationship(db_session, user: User):
    framework = Framework(
        name='framework',
        user_id=user.id,
    )

    framework.entries = {
        'key_1': 'value 1',
        'key_2': 'value 2',
        'key_3': 'value 3',
        'key_4': 'value 4',
    }

    db_session.add(framework)
    await db_session.commit()
    await db_session.refresh(user)

    user = await db_session.scalar(select(User).where(User.id == user.id))

    assert user.frameworks == [framework]
