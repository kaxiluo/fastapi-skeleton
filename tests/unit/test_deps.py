import pytest

from app.http import deps


class TrackingSession:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    async def commit(self):
        self.commits += 1

    async def rollback(self):
        self.rollbacks += 1


class FakeSessionFactory:
    """形似 async_sessionmaker：调用后返回可 async with 的对象，产出 session"""

    def __init__(self, session):
        self.session = session

    def __call__(self):
        return self

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, *exc):
        return False


async def _consume(gen):
    return await gen.__anext__()


async def test_get_db_session_commits_on_success(monkeypatch):
    session = TrackingSession()
    monkeypatch.setattr(deps, "get_session_factory", lambda: FakeSessionFactory(session))
    gen = deps.get_db_session()
    assert await gen.__anext__() is session
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()
    assert session.commits == 1
    assert session.rollbacks == 0


async def test_get_db_session_rolls_back_and_reraises(monkeypatch):
    session = TrackingSession()
    monkeypatch.setattr(deps, "get_session_factory", lambda: FakeSessionFactory(session))
    gen = deps.get_db_session()
    await gen.__anext__()
    with pytest.raises(ValueError, match="boom"):
        await gen.athrow(ValueError("boom"))
    assert session.rollbacks == 1
    assert session.commits == 0
