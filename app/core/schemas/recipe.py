from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RecipeCreateSchema(BaseModel):
    category_id: int = Field(gt=0)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    cooking_time_minutes: Optional[int] = Field(default=None, gt=0)
    image_url: Optional[str] = Field(default=None, max_length=255)


class RecipeResponseSchema(BaseModel):
    id: int = Field(default_factory=int, gt=0)
    author_id: int = Field(default_factory=int, gt=0)
    category_id: int = Field(default_factory=int, gt=0)
    name: str
    description: Optional[str]
    instructions: Optional[str]
    cooking_time_minutes: Optional[int]
    image_url: Optional[str]
    created_at: datetime


class RecipePartialUpdateSchema(BaseModel):
    category_id: Optional[int] = Field(default=None, gt=0)
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)
    cooking_time_minutes: Optional[int] = Field(default=None, gt=0)
    image_url: Optional[str] = Field(default=None, max_length=255)