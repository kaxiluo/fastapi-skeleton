import os
from pathlib import Path

import pytest

ENV_FILE = Path(".env.test")


def _load_env_file() -> None:
    # 在任何 settings 首次构造前把 .env.test 注入环境变量（优先级高于 .env）
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:  # 剥离行内注释（引号包裹的值不剥）
            value = value.split(" #", 1)[0].strip()
        if value:
            os.environ[key.strip()] = value


def pytest_collection_modifyitems(config, items):
    # 仅在 -m 恰为 integration 时注入 .env.test；
    # 不能用子串判断（"integration" in "not integration" 也为 True）
    markexpr = (config.getoption("markexpr", default="") or "").replace(" ", "")
    running_integration = markexpr == "integration"
    if running_integration and ENV_FILE.exists():
        _load_env_file()
    if not ENV_FILE.exists():
        skip = pytest.mark.skip(reason=".env.test not found; integration tests skipped")
        for item in items:
            item.add_marker(skip)


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    from alembic.config import Config

    from alembic import command

    # downgrade→upgrade 保证每个 session 从干净表 + 种子用户开始（上一轮 truncate 会清掉种子）
    cfg = Config("alembic.ini")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")


@pytest.fixture
async def client():
    from asgi_lifespan import LifespanManager
    from httpx import ASGITransport, AsyncClient

    from main import app as fastapi_app

    async with LifespanManager(fastapi_app) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


_SEED_PASSWORD_HASH: str | None = None


def _seed_password_hash() -> str:
    global _SEED_PASSWORD_HASH
    if _SEED_PASSWORD_HASH is None:
        from app.services.auth.hashing import get_password_hash

        _SEED_PASSWORD_HASH = get_password_hash("123456")
    return _SEED_PASSWORD_HASH


@pytest.fixture(autouse=True)
async def clean_tables(client):
    # 依赖 client：确保 teardown 顺序为 truncate → lifespan 关闭连接，
    # 否则 close_db 之后 get_session_factory() 会 RuntimeError
    yield
    from app.core.db import get_session_factory
    from app.core.redis import get_redis_client
    from app.models.base import Base
    from app.repositories.user_repository import UserRepository

    factory = get_session_factory()
    async with factory() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        # 重建种子用户（与迁移种子同凭据），用例顺序不再影响分支覆盖
        password = _seed_password_hash()
        await UserRepository(session).create(username="fake_user1", password=password)
        await UserRepository(session).create(username="fake_user2", password=password)
        await session.commit()
    # 测试用 Redis db 是独立 db（.env.test REDIS_DB=15），整库清空以消除限流/验证码残留
    await get_redis_client().flushdb()


@pytest.fixture
async def auth_headers(client):
    """真用户 + 真 token，覆盖 get_auth_user 全链路（users/me 用）"""
    from app.core.db import get_session_factory
    from app.repositories.user_repository import UserRepository
    from app.services.auth.hashing import get_password_hash
    from app.services.auth.jwt_helper import create_access_token

    factory = get_session_factory()
    async with factory() as session:
        user = await UserRepository(session).create(
            username="integration_authed",
            password=get_password_hash("123456"),
        )
        await session.commit()
        token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_client(client):
    """绕过 token 解析的假登录：dependency_overrides（不 monkeypatch 内部实现）"""
    from app.core.db import get_session_factory
    from app.http import deps
    from app.repositories.user_repository import UserRepository

    factory = get_session_factory()
    async with factory() as session:
        user = await UserRepository(session).create(username="override_user", password="x")
        await session.commit()

    async def override():
        return user

    from main import app as fastapi_app

    fastapi_app.dependency_overrides[deps.get_auth_user] = override
    yield client
    fastapi_app.dependency_overrides.pop(deps.get_auth_user, None)
