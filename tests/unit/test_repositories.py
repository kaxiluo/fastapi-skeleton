from app.models.user import User
from app.repositories.user_repository import UserRepository


class FakeResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value

    def scalars(self):
        return self

    def all(self):
        return self._value


class FakeSession:
    """最小假 session：只覆盖 BaseRepository 用到的接口"""

    def __init__(self, value=None):
        self.value = value
        self.added = []
        self.flushed = False
        self.refreshed = None
        self.commits = 0

    async def get(self, model, pk):
        return self.value if isinstance(self.value, User) else None

    async def execute(self, stmt):
        self.last_stmt = stmt
        return FakeResult(self.value)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True

    async def refresh(self, obj):
        self.refreshed = obj

    async def commit(self):
        self.commits += 1


def make_user(**kwargs):
    base = {
        "id": 1,
        "username": "u1",
        "password": "x",
        "state": "enabled",
        "gender": "unknown",
    }
    base.update(kwargs)
    return User(**base)


async def test_get_by_username_builds_where_clause():
    session = FakeSession(value=make_user(username="alice"))
    repo = UserRepository(session)
    user = await repo.get_by_username("alice")
    assert user.username == "alice"
    stmt = session.last_stmt
    where = stmt.whereclause
    assert "username" in str(where)


async def test_create_adds_flushes_and_refreshes_without_commit():
    session = FakeSession()
    repo = UserRepository(session)
    user = await repo.create(username="bob", password="hashed")
    assert session.added == [user]
    assert session.flushed
    assert session.refreshed is user
    assert user.username == "bob"
    assert session.commits == 0  # 仓储永不 commit


async def test_get_or_none_none():
    session = FakeSession(value=None)
    repo = UserRepository(session)
    assert await repo.get_or_none(username="nobody") is None
