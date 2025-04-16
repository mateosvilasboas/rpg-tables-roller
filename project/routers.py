from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import User as UserModel
from .schemas import (UserSchema,
                      UserList,
                      FilterPage)


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=UserList)
async def get_users(
    filter_users: Annotated[FilterPage, Query()], session: AsyncSession = Depends(get_db)
):
    query = await session.scalars(
        select(UserModel).offset(filter_users.offset).limit(filter_users.limit))
    
    users = query.all()

    return {'users': users}


@router.post("/", response_model=UserSchema)
async def create_user(user: UserSchema, session: AsyncSession = Depends(get_db)):
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
        email=user.email,)
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user

        