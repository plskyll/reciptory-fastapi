

from typing import Any, AsyncGenerator


import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


from app.core.models.base import BaseModel
from app.main import app
from app.core.settings import db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"




@pytest.fixture(scope="session")
async def db_engine():
   engine = create_async_engine(TEST_DATABASE_URL, echo=False)
   async with engine.begin() as conn:
       await conn.run_sync(BaseModel.metadata.create_all)
   yield engine
   await engine.dispose()




@pytest.fixture(scope="function")
async def db_session(db_engine):
   async_session = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
   async with async_session() as session:
       yield session
       await session.rollback()




@pytest.fixture(autouse=True)
async def clear_db(db_session: AsyncSession):
   for table in reversed(BaseModel.metadata.sorted_tables):
       await db_session.execute(table.delete())
   await db_session.commit()




@pytest_asyncio.fixture()
async def client(db_session, monkeypatch) -> AsyncGenerator[AsyncClient, Any]:
   async def override_get_session():
       async with db_session as session:
           yield session


   app.dependency_overrides[db.get_session] = override_get_session


   async with LifespanManager(app):
       async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
           yield client
