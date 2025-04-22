from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import User as UserModel
from .schemas import (UserSchema,
                      UserList,
                      UserPublic,
                      Message,
                      FilterPage)

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

session = Annotated[AsyncSession, Depends(get_db)]

@router.get("/", response_model=UserList)
async def get_users(
    filter_users: Annotated[FilterPage, Query()], session: session
):
    query = await session.scalars(
        select(UserModel).offset(filter_users.offset).limit(filter_users.limit))
    
    users = query.all()

    return {'users': users}


@router.post("/", response_model=UserPublic)
async def create_user(
    user: UserSchema, session: session
):
    db_user = await session.scalar(select(UserModel).where(
        UserModel.email == user.email
        )
    )

    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    db_user = UserModel(
        name=user.name,
        email=user.email,
    )
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user

@router.put("/", response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: session
):
    db_user = await session.scalar(select(UserModel).where(UserModel.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )
    
    try:
        db_user.name = user.name
        db_user.email = user.email
        await session.commit()
        await session.refresh(db_user)

        return db_user
    
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )

@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: int,
    session: session
):
    db_user = await session.scalar(select(UserModel).where(UserModel.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )
    
    await session.delete(db_user)
    await session.commit()

    return {'message': 'User deleted'}