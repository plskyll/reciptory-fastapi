from typing import Annotated, Sequence

import sqlalchemy
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core import auth
from app.core.models.recipe import RecipeModel
from app.core.models.user import UserModel
from app.core.schemas.recipe import RecipeResponseSchema, RecipeCreateSchema, RecipePartialUpdateSchema
from app.core.settings.db import db
from fastapi import APIRouter


SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post(
    path="/",
    response_model=RecipeResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(recipe: RecipeCreateSchema, session: SessionDepend, current_user: UserModel = Depends(auth.access_token_required)):

    new_recipe = RecipeModel(
        author_id=current_user.id,
        category_id=recipe.category_id,
        name=recipe.name,
        description=recipe.description,
        instructions=recipe.instructions,
        cooking_time_minutes=recipe.cooking_time_minutes,
        image_url=recipe.image_url,
    )
    session.add(new_recipe)
    await session.commit()
    await session.refresh(new_recipe)
    return new_recipe


@router.get(
    "/",
    response_model=list[RecipeResponseSchema],
)
async def get_recipes(session: SessionDepend) -> Sequence[RecipeModel]:
    query = sqlalchemy.select(RecipeModel)
    result = await session.execute(query)
    recipes = result.scalars().all()
    return recipes


@router.get(
    path="/{recipe_id}",
    response_model=RecipeResponseSchema,
)
async def get_recipe(recipe_id: int, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(RecipeModel).where(RecipeModel.id == recipe_id))
    recipe = result.scalars().first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put(
    path="/{recipe_id}",
    response_model=RecipeResponseSchema,
)
async def update_recipe(recipe_id: int, recipe: RecipeCreateSchema, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(RecipeModel).where(RecipeModel.id == recipe_id))
    existing_recipe = result.scalars().first()
    if not existing_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    for field, value in  recipe.model_dump().items():
        setattr(existing_recipe, field, value)
    session.add(existing_recipe)

    await session.commit()
    await session.refresh(existing_recipe)
    return existing_recipe


@router.patch(
    path="/{recipe_id}",
    response_model=RecipeResponseSchema,
)
async def partial_update_recipe(recipe_id: int, recipe: RecipePartialUpdateSchema, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(RecipeModel).where(RecipeModel.id == recipe_id))
    existing_recipe = result.scalars().first()
    if not existing_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    for field, value in  recipe.model_dump().items():
        setattr(existing_recipe, field, value)
    session.add(existing_recipe)

    await session.commit()
    await session.refresh(existing_recipe)
    return existing_recipe


@router.delete(
    path="/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.access_token_required)]
)
async def delete_recipe(recipe_id: int, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(RecipeModel).where(RecipeModel.id == recipe_id))
    existing_recipe = result.scalars().first()
    if not existing_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    await session.delete(existing_recipe)
    await session.commit()
    return None