from typing import Annotated, Sequence

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth
from app.core.models.recipe_ingredient import RecipeIngredientModel
from app.core.schemas.recipe_ingredient import RecipeIngredientResponseSchema, RecipeIngredientCreateSchema, RecipeIngredientPartialUpdateSchema
from app.core.settings.db import db

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]

router = APIRouter(prefix="/recipe_ingredients", tags=["recipe_ingredients"])


@router.post(
    path="/",
    response_model=RecipeIngredientResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth.access_token_required)]
)
async def create_recipe_ingredient(
        recipe_ingredient: RecipeIngredientCreateSchema,
        session: SessionDepend,
):
    query = sqlalchemy.select(RecipeIngredientModel).where(
        RecipeIngredientModel.recipe_id == recipe_ingredient.recipe_id,
        RecipeIngredientModel.ingredient_id == recipe_ingredient.ingredient_id
    )
    result = await session.execute(query)
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This ingredient is already added to the recipe"
        )

    new_item = RecipeIngredientModel(
        recipe_id=recipe_ingredient.recipe_id,
        ingredient_id=recipe_ingredient.ingredient_id,
        amount=recipe_ingredient.amount,
    )
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item


@router.get(
    "/",
    response_model=list[RecipeIngredientResponseSchema],
)
async def get_recipe_ingredients(session: SessionDepend) -> Sequence[RecipeIngredientModel]:
    query = sqlalchemy.select(RecipeIngredientModel)
    result = await session.execute(query)
    items = result.scalars().all()
    return items


@router.get(
    path="/{recipe_id}/{ingredient_id}",
    response_model=RecipeIngredientResponseSchema,
)
async def get_recipe_ingredient(
        recipe_id: int,
        ingredient_id: int,
        session: SessionDepend
):
    query = sqlalchemy.select(RecipeIngredientModel).where(
        RecipeIngredientModel.recipe_id == recipe_id,
        RecipeIngredientModel.ingredient_id == ingredient_id
    )
    result = await session.execute(query)
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail="Recipe ingredient not found")

    return item


@router.patch(
    path="/{recipe_id}/{ingredient_id}",
    response_model=RecipeIngredientResponseSchema,
)
async def partial_update_recipe_ingredient(
        recipe_id: int,
        ingredient_id: int,
        update_data: RecipeIngredientPartialUpdateSchema,
        session: SessionDepend,
        dependencies=[Depends(auth.access_token_required)]
):
    query = sqlalchemy.select(RecipeIngredientModel).where(
        RecipeIngredientModel.recipe_id == recipe_id,
        RecipeIngredientModel.ingredient_id == ingredient_id
    )
    result = await session.execute(query)
    existing_item = result.scalars().first()

    if not existing_item:
        raise HTTPException(status_code=404, detail="Recipe ingredient not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(existing_item, field, value)

    session.add(existing_item)
    await session.commit()
    await session.refresh(existing_item)
    return existing_item


@router.delete(
    path="/{recipe_id}/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.access_token_required)]
)
async def delete_recipe_ingredient(
        recipe_id: int,
        ingredient_id: int,
        session: SessionDepend
):
    query = sqlalchemy.select(RecipeIngredientModel).where(
        RecipeIngredientModel.recipe_id == recipe_id,
        RecipeIngredientModel.ingredient_id == ingredient_id
    )
    result = await session.execute(query)
    existing_item = result.scalars().first()

    if not existing_item:
        raise HTTPException(status_code=404, detail="Recipe ingredient not found")

    await session.delete(existing_item)
    await session.commit()
    return None