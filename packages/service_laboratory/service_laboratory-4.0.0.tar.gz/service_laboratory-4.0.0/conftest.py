import asyncio
from collections.abc import AsyncIterator
from typing import Any, AsyncGenerator

from advanced_alchemy.base import UUIDAuditBase
from litestar import Litestar
from litestar.testing import AsyncTestClient
import pytest
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.auth import auth_router
from src.core.database import sqlalchemy_plugin
from src.core.settings import settings


@pytest.fixture(scope="session")
def application():
    application = Litestar(
        route_handlers=[auth_router],
        plugins=[sqlalchemy_plugin],
    )
    return application


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="function")
async def test_client(application) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app=application) as client:
        yield client


@pytest.fixture(scope="session")
async def db():
    yield "ok"
    print("clear")


@pytest.fixture(scope="session")
async def db_session() -> AsyncGenerator[AsyncSession, Any]:
    engine = create_async_engine(url=settings.db_url)

    metadata = UUIDAuditBase.registry.metadata
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    # create async engine
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    # clear database
    async with engine.begin() as conn:
        meta = sqlalchemy.MetaData()
        await conn.run_sync(meta.reflect)
        await conn.run_sync(meta.drop_all)
