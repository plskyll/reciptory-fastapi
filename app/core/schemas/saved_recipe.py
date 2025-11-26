from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SavedRecipeCreateSchema(BaseModel):
    recipe_id: int = Field(default_factory=int, gt=0)


class SavedRecipeResponseSchema(BaseModel):
    id: int = Field(default_factory=int, gt=0)
    user_id: int = Field(default_factory=int, gt=0)
    recipe_id: int = Field(default_factory=int, gt=0)
    saved_at: datetime


class SavedRecipePartialUpdateSchema(BaseModel):
    recipe_id: Optional[int] = Field(default=None, gt=0)

