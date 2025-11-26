from typing import Annotated, Sequence

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth
from app.core.auth import access_token_required as get_current_user
from app.core.models.user import UserModel
from app.core.models.saved_recipe import SavedRecipeModel
from app.core.schemas.saved_recipe import SavedRecipeResponseSchema, SavedRecipeCreateSchema
from app.core.settings.db import db


SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]

router = APIRouter(prefix="/saved_recipes", tags=["saved_recipes"])


@router.post(
    path="/",
    response_model=SavedRecipeResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_saved_recipe(
        saved_recipe: SavedRecipeCreateSchema,
        session: SessionDepend,
        current_user: UserModel = Depends(get_current_user)  #
):
    new_saved_recipe = SavedRecipeModel(
        user_id=current_user.id,
        recipe_id=saved_recipe.recipe_id
    )
    session.add(new_saved_recipe)
    await session.commit()
    await session.refresh(new_saved_recipe)
    return new_saved_recipe


@router.get(
    "/",
    response_model=list[SavedRecipeResponseSchema],
)
async def get_saved_recipes(session: SessionDepend) -> Sequence[SavedRecipeModel]:
    query = sqlalchemy.select(SavedRecipeModel)
    result = await session.execute(query)
    saved_recipes = result.scalars().all()
    return saved_recipes


@router.get(
    path="/{saved_recipe_id}",
    response_model=SavedRecipeResponseSchema,
)
async def get_saved_recipe(saved_recipe_id: int, session: SessionDepend):
    query = sqlalchemy.select(SavedRecipeModel).where(SavedRecipeModel.id == saved_recipe_id)
    result = await session.execute(query)
    saved_recipe = result.scalars().first()

    if not saved_recipe:
        raise HTTPException(status_code=404, detail="Saved recipe not found")

    return saved_recipe


@router.delete(
    path="/{saved_recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.access_token_required)]
)
async def delete_saved_recipe(saved_recipe_id: int, session: SessionDepend):
    query = sqlalchemy.select(SavedRecipeModel).where(SavedRecipeModel.id == saved_recipe_id)
    result = await session.execute(query)
    existing_saved_recipe = result.scalars().first()

    if not existing_saved_recipe:
        raise HTTPException(status_code=404, detail="Saved recipe not found")

    await session.delete(existing_saved_recipe)
    await session.commit()
    return None