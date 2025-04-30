from datetime import datetime
from http import HTTPStatus
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from redis import asyncio as redis_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project.config import settings
from project.database import get_db
from project.models import User
from project.redis import get_redis
from project.schemas import Message, Token
from project.security.auth import (
    create_access_token,
    get_current_user,
    oauth2_scheme,
    verify_password,
)
from project.utils.constants import ErrorMessages

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={404: {'detail': ErrorMessages.NOT_FOUND}},
)

Session = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[redis_asyncio.Redis, Depends(get_redis)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]
TokenDependecy = Annotated[str, Depends(oauth2_scheme)]


@router.post('/token', response_model=Token)
async def login(form_data: OAuth2Form, session: Session):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.WRONG_EMAIL_OR_PASSWORD,
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.WRONG_EMAIL_OR_PASSWORD,
        )

    access_token = create_access_token(data={'sub': user.email})
    token_type = 'bearer'

    token = {'access_token': access_token, 'token_type': token_type}

    return token


@router.post('/revoke_token', response_model=Message)
async def logout(
    token: TokenDependecy, redis: RedisClient, current_user: CurrentUser
):
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    email = payload.get('sub')
    if email != current_user.email:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=ErrorMessages.FORBIDDEN,
        )

    exp = payload.get('exp', 0)
    current_time = datetime.now().timestamp()
    ttl = max(1, int(exp - current_time))

    await redis.set(f'denylist:{token}', '1', ex=ttl)

    return {'detail': ErrorMessages.LOGOUT_SUCCESS}


@router.post('/refresh_token', response_model=Token)
async def refresh_token(
    token: TokenDependecy, redis: RedisClient, current_user: CurrentUser
):
    access_token = create_access_token(data={'sub': current_user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
