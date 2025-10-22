from advanced_alchemy.base import UUIDAuditBase
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .settings import settings

config = SQLAlchemyAsyncConfig(
    connection_string=settings.db_url, create_all=True, metadata=UUIDAuditBase.metadata
)
sqlalchemy_plugin = SQLAlchemyPlugin(config=config)


engine = create_async_engine(settings.db_url, echo=False)
session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
