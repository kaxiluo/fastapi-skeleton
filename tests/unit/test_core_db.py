import pytest

from app.core import db
from app.core import redis as core_redis


def test_db_not_initialized_raises():
    db._engine = None
    db._session_factory = None
    with pytest.raises(RuntimeError, match="init_db"):
        db.get_engine()
    with pytest.raises(RuntimeError, match="init_db"):
        db.get_session_factory()


def test_redis_not_initialized_raises():
    core_redis._client = None
    with pytest.raises(RuntimeError, match="init_redis"):
        core_redis.get_redis_client()


async def test_db_init_close_cycle(monkeypatch):
    from config.database import get_database_settings

    get_database_settings.cache_clear()  # 绕过 lru_cache 与本机 .env 的干扰
    monkeypatch.setenv("DB_POOL_SIZE", "7")
    await db.init_db()
    try:
        engine = db.get_engine()
        factory = db.get_session_factory()
        assert engine.pool.size() == 7
        async with factory() as session:
            assert session.bind is engine
    finally:
        await db.close_db()
        get_database_settings.cache_clear()
    assert db._engine is None
