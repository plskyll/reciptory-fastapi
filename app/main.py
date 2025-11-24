from typing import Union
from fastapi import FastAPI

from app.core.models.base import BaseModel
from app.core.settings.db import Database
from contextlib import asynccontextmanager


DATABASE_URL = "sqlite+aiosqlite:///./test.db"

db = Database(url=DATABASE_URL)

@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
   await db.connect()
   async with db.engine.begin() as connection:
       await connection.run_sync(BaseModel.metadata.create_all)
   yield
   await db.disconnect()

app = FastAPI(lifespan=lifespan)

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