from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class RecipeIngredientModel(BaseModel):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), primary_key=True)

    amount: Mapped[str] = mapped_column(String(50))

    recipe: Mapped["RecipeModel"] = relationship(back_populates="ingredients")
    ingredient: Mapped["IngredientModel"] = relationship(back_populates="recipes")