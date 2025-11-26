from typing import Optional

from pydantic import BaseModel, Field


class RecipeIngredientCreateSchema(BaseModel):
    recipe_id: int = Field(default_factory=int, gt=0)
    ingredient_id: int = Field(default_factory=int, gt=0)
    amount: str = Field(max_length=50)


class RecipeIngredientResponseSchema(BaseModel):
    id: int = Field(default_factory=int, gt=0)
    recipe_id: int = Field(default_factory=int, gt=0)
    ingredient_id: int = Field(default_factory=int, gt=0)
    amount: str


class RecipeIngredientPartialUpdateSchema(BaseModel):
    recipe_id: Optional[int] = Field(default=None, gt=0)
    ingredient_id: Optional[int] = Field(default=None, gt=0)
    amount: Optional[str] = Field(default=None, max_length=50)

