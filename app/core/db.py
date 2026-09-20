from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.utils.timezone_utils import mysql_timezone_offset
from config.database import get_database_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database engine not initialized; call init_db() first")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized; call init_db() first")
    return _session_factory


async def init_db() -> None:
    global _engine, _session_factory
    settings = get_database_settings()
    _engine = create_async_engine(
        settings.url,
        pool_pre_ping=True,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_recycle=settings.pool_recycle,
        connect_args={
            "charset": "utf8mb4",
            "autocommit": False,
            "init_command": f"SET time_zone = '{mysql_timezone_offset()}'",
        },
    )
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def close_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
