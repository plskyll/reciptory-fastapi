from typing import Union
from fastapi import FastAPI

from app.core.models.base import BaseModel
from app.core.settings.db import Database
from contextlib import asynccontextmanager
from app.core.settings.db import db

from app.core.routers import category, ingredient, recipe, recipe_ingredient, saved_recipe, user, auth
from app.core.models import (
    user as user_model,
    category as category_model,
    recipe as recipe_model,
    ingredient as ingredient_model,
    recipe_ingredient as recipe_ingredient_model,
    saved_recipe as saved_recipe_model
)

@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
   await db.connect()
   async with db.engine.begin() as connection:
       await connection.run_sync(BaseModel.metadata.create_all)
   yield
   await db.disconnect()

app = FastAPI(lifespan=lifespan)


app.include_router(category.router)
app.include_router(ingredient.router)
app.include_router(recipe.router)
app.include_router(recipe_ingredient.router)
app.include_router(saved_recipe.router)
app.include_router(user.router)
app.include_router(auth.router)
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get(path="/health", tags=["System"])
async def health():
   ok = await db.ping()
   return {"status": "ok" if ok else "error"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        port=8000,
        log_level="info",
        use_colors=False,
    )