from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreateSchema(BaseModel):
    username: str = Field(max_length=50)
    email: str = Field(max_length=100)
    password: str = Field(max_length=255)


class UserResponseSchema(BaseModel):
    id: int = Field(default_factory=int, gt=0)
    username: str
    email: str
    created_at: datetime


class UserPartialUpdateSchema(BaseModel):
    username: Optional[str] = Field(max_length=50)
    email: Optional[str] = Field(max_length=100)
    password: Optional[str] = Field(max_length=255)

