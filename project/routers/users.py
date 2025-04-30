from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from project.database import get_db
from project.models import User
from project.schemas import (
    Message,
    UserPublic,
    UserPublicList,
    UserSchemaCreate,
    UserSchemaUpdate,
)
from project.security.auth import get_current_user, get_password_hash
from project.utils.constants import ErrorMessages

Session = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {'detail': ErrorMessages.NOT_FOUND}},
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
                detail=ErrorMessages.EMAIL_EXISTS,
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(name=user.name, email=user.email, password=hashed_password)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.put('/', response_model=UserPublic)
async def update_user(
    user: UserSchemaUpdate,
    session: Session,
    current_user: CurrentUser,
):
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
            detail=ErrorMessages.EMAIL_EXISTS,
        )


@router.delete('/', response_model=Message)
async def delete_user(session: Session, current_user: CurrentUser):
    if current_user.is_deleted:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.USER_NOT_FOUND,
        )

    current_user.soft_delete()
    await session.commit()

    return {'detail': ErrorMessages.USER_DELETED}


@router.put('/restore/{user_id}', response_model=UserPublic)
async def restore_deleted_user(
    user_id: int, session: Session, current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=ErrorMessages.FORBIDDEN,
        )

    if not current_user.is_deleted:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorMessages.USER_NOT_DELETED,
        )

    current_user.restore()
    await session.commit()

    return current_user
