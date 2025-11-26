from typing import Annotated, Sequence

import sqlalchemy
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core import auth
from app.core.models.user import UserModel
from app.core.schemas.user import UserResponseSchema, UserCreateSchema, UserPartialUpdateSchema
from app.core.settings.db import db
from app.core.utils import get_password_hash
from fastapi import APIRouter

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    path="/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreateSchema, session: SessionDepend):
    new_user = UserModel(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.get(
    "/",
    response_model=list[UserResponseSchema],
)
async def get_users(session: SessionDepend) -> Sequence[UserModel]:
    query = sqlalchemy.select(UserModel)
    result = await session.execute(query)
    users = result.scalars().all()
    return users


@router.get(
    path="/{user_id}",
    response_model=UserResponseSchema,
)
async def get_user(user_id: int, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    path="/{user_id}",
    response_model=UserResponseSchema,
)
async def partial_update_user(user_id: int, user: UserPartialUpdateSchema, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(UserModel).where(UserModel.id == user_id))
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user.model_dump().items():
        if value is not None:
            if field == "password":
                value = get_password_hash(value)
            setattr(existing_user, field, value)

    session.add(existing_user)
    await session.commit()
    await session.refresh(existing_user)
    return existing_user


@router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.access_token_required)]
)
async def delete_user(user_id: int, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(UserModel).where(UserModel.id == user_id))
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(existing_user)
    await session.commit()
    return None