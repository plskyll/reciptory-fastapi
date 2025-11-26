from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token
from app.core.models.user import UserModel
from app.core.settings.db import db
from app.core.utils import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]


@router.post("/login")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDepend
):
    query = select(UserModel).where(UserModel.email == form_data.username)
    result = await session.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}