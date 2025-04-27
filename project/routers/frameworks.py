from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Framework, User
from ..schemas import FrameworkPublic, FrameworkSchema
from ..security import get_current_user

Session = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix='/frameworks',
    tags=['frameworks'],
    responses={404: {'detail': 'Not found'}},
)


# @router.get('/', response_model=UserList)
# async def get_users(
#     filter_users: Annotated[FilterPage, Query()], session: Session
# ):
#     query = await session.scalars(
#         select(User)
#         .where(User.is_deleted == False)  # noqa
#         .offset(filter_users.offset)
#         .limit(filter_users.limit)
#     )

#     users = query.all()

#     return {'users': users}


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
            detail='Framework must have at least one entry',
        )

    db_framework.entries = framework.entries

    session.add(db_framework)
    await session.commit()
    await session.refresh(db_framework)

    return db_framework


# @router.put('/{user_id}', response_model=UserPublic)
# async def update_user(
#     user_id: int,
#     user: UserSchemaUpdate,
#     session: Session,
#     current_user: CurrentUser,
# ):
#     if current_user.id != user_id:
#         raise HTTPException(
#             status_code=HTTPStatus.FORBIDDEN,
#             detail='Not enough permissions',
#         )

#     try:
#         current_user.name = user.name
#         current_user.email = user.email

#         if user.password:
#             current_user.password = get_password_hash(user.password)

#         await session.commit()
#         await session.refresh(current_user)

#         return current_user

#     except IntegrityError:
#         raise HTTPException(
#             status_code=HTTPStatus.CONFLICT,
#             detail='Email already exists',
#         )


# @router.delete('/{user_id}', response_model=Message)
# async def delete_user(
#     user_id: int, session: Session, current_user: CurrentUser
# ):
#     if current_user.id != user_id:
#         raise HTTPException(
#             status_code=HTTPStatus.FORBIDDEN,
#             detail='Not enough permissions',
#         )

#     if current_user.is_deleted:
#         raise HTTPException(
#             status_code=HTTPStatus.BAD_REQUEST, detail='User already deleted'
#         )

#     current_user.soft_delete()
#     await session.commit()

#     return {'message': 'User deleted'}
