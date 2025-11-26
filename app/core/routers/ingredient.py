from typing import Annotated, Sequence

import sqlalchemy
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core import auth
from app.core.models.ingredient import IngredientModel
from app.core.schemas.ingredient import IngredientResponseSchema, IngredientCreateSchema, IngredientPartialUpdateSchema
from app.core.settings.db import db
from fastapi import APIRouter

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post(
    path="/",
    response_model=IngredientResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_ingredient(ingredient: IngredientCreateSchema, session: SessionDepend):
    new_ingredient = IngredientModel(
        name=ingredient.name,
        calories_per_100g=ingredient.calories_per_100g
    )
    session.add(new_ingredient)
    await session.commit()
    await session.refresh(new_ingredient)
    return new_ingredient


@router.get(
    "/",
    response_model=list[IngredientResponseSchema],
)
async def get_ingredients(session: SessionDepend) -> Sequence[IngredientModel]:
    query = sqlalchemy.select(IngredientModel)
    result = await session.execute(query)
    ingredients = result.scalars().all()
    return ingredients


@router.get(
    path="/{ingredient_id}",
    response_model=IngredientResponseSchema,
)
async def get_ingredient(ingredient_id: int, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(IngredientModel).where(IngredientModel.id == ingredient_id))
    ingredient = result.scalars().first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.put(
    path="/{ingredient_id}",
    response_model=IngredientResponseSchema,
)
async def update_ingredient(ingredient_id: int, ingredient: IngredientCreateSchema, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(IngredientModel).where(IngredientModel.id == ingredient_id))
    existing_ingredient = result.scalars().first()
    if not existing_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    for field, value in  ingredient.model_dump().items():
        setattr(existing_ingredient, field, value)
    session.add(existing_ingredient)

    await session.commit()
    await session.refresh(existing_ingredient)
    return existing_ingredient


@router.patch(
    path="/{ingredient_id}",
    response_model=IngredientResponseSchema,
)
async def partial_update_ingredient(ingredient_id: int, ingredient: IngredientPartialUpdateSchema, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(IngredientModel).where(IngredientModel.id == ingredient_id))
    existing_ingredient = result.scalars().first()
    if not existing_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    for field, value in  ingredient.model_dump().items():
        setattr(existing_ingredient, field, value)
    session.add(existing_ingredient)

    await session.commit()
    await session.refresh(existing_ingredient)
    return existing_ingredient


@router.delete(
    path="/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.access_token_required)]
)
async def delete_ingredient(ingredient_id: int, session: SessionDepend):
    result = await session.execute(sqlalchemy.select(IngredientModel).where(IngredientModel.id == ingredient_id))
    existing_ingredient = result.scalars().first()
    if not existing_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    await session.delete(existing_ingredient)
    await session.commit()
    return None