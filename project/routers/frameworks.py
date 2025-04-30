from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from project.database import get_db
from project.models import Framework, User
from project.schemas import (
    FrameworkPublic,
    FrameworkPublicList,
    FrameworkSchema,
    Message,
)
from project.security.auth import get_current_user
from project.utils.constants import ErrorMessages

Session = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix='/frameworks',
    tags=['frameworks'],
    responses={404: {'detail': ErrorMessages.NOT_FOUND}},
)


@router.get('/', response_model=FrameworkPublicList)
async def get_frameworks(
    session: Session,
    current_user: CurrentUser,
):
    frameworks = await session.scalars(
        select(Framework).where(
            and_(
                Framework.user_id == current_user.id,
                Framework.is_deleted == False,  # noqa
            )
        )
    )
    
    query = frameworks.all()

    return {"frameworks": query}


@router.get('/{framework_id}', response_model=FrameworkPublic)
async def get_framework(
    framework_id: int,
    session: Session,
    current_user: CurrentUser,
):
    framework = await session.scalar(
        select(Framework).where(
            and_(
                Framework.id == framework_id,
                Framework.user_id == current_user.id,
                Framework.is_deleted == False,  # noqa
            )
        )
    )

    if not framework:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.FRAMEWORK_NOT_FOUND,
        )

    return framework


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=FrameworkPublic
)
async def create_framework(
    framework: FrameworkSchema, session: Session, current_user: CurrentUser
):
    db_framework = Framework(
        name=framework.name,
        user_id=current_user.id,
    )

    if not framework.entries:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorMessages.FRAMEWORK_EMPTY_ENTRIES,
        )

    db_framework.entries = framework.entries

    session.add(db_framework)
    await session.commit()
    await session.refresh(db_framework)

    return db_framework


@router.put('/{framework_id}', response_model=FrameworkPublic)
async def update_framework(
    framework_id: int,
    framework: FrameworkSchema,
    session: Session,
    current_user: CurrentUser,
):
    db_framework = await session.scalar(
        select(Framework).where(
            and_(
                Framework.id == framework_id,
                Framework.user_id == current_user.id,
                Framework.is_deleted == False,  # noqa
            )
        )
    )

    if not db_framework:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.FRAMEWORK_NOT_FOUND,
        )

    db_framework.name = framework.name
    db_framework.entries = framework.entries

    await session.commit()
    await session.refresh(current_user)

    return db_framework


@router.delete('/{framework_id}', response_model=Message)
async def delete_framework(
    framework_id: int,
    session: Session,
    current_user: CurrentUser,
):
    db_framework = await session.scalar(
        select(Framework).where(
            and_(
                Framework.id == framework_id,
                Framework.user_id == current_user.id,
                Framework.is_deleted == False,  # noqa
            )
        )
    )

    if not db_framework:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.FRAMEWORK_NOT_FOUND,
        )

    db_framework.soft_delete()
    await session.commit()

    return {'detail': 'Framework deleted'}
