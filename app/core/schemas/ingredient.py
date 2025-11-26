from typing import Optional

from pydantic import BaseModel, Field


class IngredientCreateSchema(BaseModel):
    name: str = Field(max_length=100)
    calories_per_100g: Optional[int] = Field(default=None)


class IngredientResponseSchema(BaseModel):
    id: int = Field(default_factory=int, gt=0)
    name: str
    calories_per_100g: Optional[int]


class IngredientPartialUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    calories_per_100g: Optional[int] = Field(default=None)
