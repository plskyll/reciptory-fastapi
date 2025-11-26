from typing import List, Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import BaseModel

class IngredientModel(BaseModel):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    calories_per_100g: Mapped[Optional[int]] = mapped_column(Integer)

    recipes: Mapped[List["RecipeIngredientModel"]] = relationship(back_populates="ingredient")