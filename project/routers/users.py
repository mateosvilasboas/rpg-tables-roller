from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import User
from ..schemas import (
    Message,
    UserPublic,
    UserPublicList,
    UserSchemaCreate,
    UserSchemaUpdate,
)
from ..security.auth import get_current_user, get_password_hash

Session = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {'detail': 'Not found'}},
)


@router.get('/', response_model=UserPublicList)
async def get_users(session: Session):
    query = await session.scalars(
        select(User).where(
            and_(User.is_deleted == False)  # noqa
        )
    )

    users = query.all()

    return {'users': users}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchemaCreate, session: Session):
    db_user = await session.scalar(
        select(User).where(User.email == user.email)
    )

    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(name=user.name, email=user.email, password=hashed_password)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchemaUpdate,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    try:
        current_user.name = user.name
        current_user.email = user.email

        if user.password:
            current_user.password = get_password_hash(user.password)

        current_user.set_updated_at()

        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )


@router.delete('/{user_id}', response_model=Message)
async def delete_user(
    user_id: int, session: Session, current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    if current_user.is_deleted:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User already deleted'
        )

    current_user.soft_delete()
    await session.commit()

    return {'detail': 'User deleted'}


@router.put('/restore/{user_id}', response_model=UserPublic)
async def restore_deleted_user(
    user_id: int, session: Session, current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    if not current_user.is_deleted:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User is not deleted'
        )

    current_user.restore()
    await session.commit()

    return current_user
