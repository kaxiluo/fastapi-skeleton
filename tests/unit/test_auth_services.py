from datetime import UTC, datetime, timedelta

import jwt as pyjwt
import pytest

from app.services.auth import hashing, jwt_helper

UNIT_TEST_SECRET = "unit-test-secret-that-is-long-enough-32"


@pytest.fixture(autouse=True)
def auth_secret(monkeypatch):
    from config.auth import get_auth_settings

    monkeypatch.setenv("AUTH_JWT_SECRET", UNIT_TEST_SECRET)
    get_auth_settings.cache_clear()
    yield
    get_auth_settings.cache_clear()


def test_hash_and_verify_password_roundtrip():
    hashed = hashing.get_password_hash("123456")
    assert hashed.startswith("$2")  # bcrypt 格式
    assert hashing.verify_password("123456", hashed)
    assert not hashing.verify_password("wrong", hashed)


def test_hash_verifies_legacy_passlib_bcrypt():
    # 存量库中 passlib 生成的哈希（明文 123456），pwdlib 必须兼容
    legacy = "$2b$12$qn3Hjh8zCfYsSnbqHBq63eXjaTwWs4r/SH3yLycDAOTFUi80em6Ju"
    assert hashing.verify_password("123456", legacy)


def test_create_token_uses_utc_now():
    token = jwt_helper.create_access_token(42)
    payload = pyjwt.decode(token, UNIT_TEST_SECRET, algorithms=["HS256"])
    assert payload["sub"] == "42"
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    assert exp > datetime.now(UTC)


def test_token_expired():
    token = jwt_helper.create_access_token(1, expires_delta=timedelta(seconds=-10))
    with pytest.raises(pyjwt.ExpiredSignatureError):
        jwt_helper.get_payload_by_token(token)


def test_token_invalid():
    with pytest.raises(pyjwt.InvalidTokenError):
        jwt_helper.get_payload_by_token("not-a-jwt")


class FakePipeline:
    def __init__(self, redis):
        self.redis = redis
        self.ops = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def incr(self, key):
        self.ops.append(("incr", key))
        return self

    def expire(self, key, ttl):
        self.ops.append(("expire", key, ttl))
        return self

    async def execute(self):
        results = []
        for op in self.ops:
            if op[0] == "incr":
                results.append(await self.redis.incr(op[1]))
            else:
                results.append(await self.redis.expire(op[1], op[2]))
        return results


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.expires = {}

    def pipeline(self, transaction=True):
        return FakePipeline(self)

    async def set(self, key, value, ex=None):
        self.store[key] = str(value)
        if ex is not None:
            self.expires[key] = ex

    async def get(self, key):
        return self.store.get(key)

    async def delete(self, key):
        self.store.pop(key, None)

    async def incr(self, key):
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    async def expire(self, key, ttl):
        self.expires[key] = ttl
        return True


class FakeUserRepo:
    def __init__(self, user=None):
        self.user = user

    async def get_by_username(self, username):
        return self.user

    async def get_by_cellphone(self, cellphone):
        return self.user

    async def create(self, **kwargs):
        from tests.unit.test_repositories import make_user

        kwargs.setdefault("id", 99)
        return make_user(**kwargs)


async def test_check_correct_and_consumed(monkeypatch):
    from app.core import redis as core_redis
    from app.services.auth import random_code_verifier

    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)
    code = await random_code_verifier.make("13800138000")
    assert fake.store["verification:cellphone:13800138000"] == code
    assert await random_code_verifier.check("13800138000", code)
    assert "verification:cellphone:13800138000" not in fake.store  # 通过即删
    assert not await random_code_verifier.check("13800138000", "000000")


async def test_debug_code_allowlist(monkeypatch):
    from app.core import redis as core_redis
    from app.services.auth import random_code_verifier
    from config.settings import get_app_settings

    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("AUTH_DEBUG_VERIFICATION_CODE", "747380")
    get_app_settings.cache_clear()
    assert await random_code_verifier.check("13800138000", "747380")
    get_app_settings.cache_clear()


async def test_debug_code_rejected_in_production(monkeypatch):
    from app.core import redis as core_redis
    from app.services.auth import random_code_verifier
    from config.settings import get_app_settings

    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_DEBUG_VERIFICATION_CODE", "747380")
    get_app_settings.cache_clear()
    assert not await random_code_verifier.check("13800138000", "747380")
    get_app_settings.cache_clear()


async def test_cellphone_grant_rejects_wrong_code(monkeypatch):
    from app.core import redis as core_redis
    from app.exceptions import AuthenticationError
    from app.services.auth.grant import CellphoneGrant
    from app.services.auth.oauth2_schema import OAuth2CellphoneRequest

    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)

    request = OAuth2CellphoneRequest(cellphone="13800138000", verification_code="000000")
    with pytest.raises(AuthenticationError):
        await CellphoneGrant(request, session=None).respond()


async def test_cellphone_grant_correct_code_autoregisters(monkeypatch):
    from app.core import redis as core_redis
    from app.services.auth import random_code_verifier
    from app.services.auth.grant import CellphoneGrant
    from app.services.auth.oauth2_schema import OAuth2CellphoneRequest

    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)
    code = await random_code_verifier.make("13800138000")

    created = {}

    class Repo(FakeUserRepo):
        async def get_by_cellphone(self, cellphone):
            return None

        async def create(self, **kwargs):
            created.update(kwargs)
            from tests.unit.test_repositories import make_user

            return make_user(**kwargs)

    import app.services.auth.grant as grant_mod

    monkeypatch.setattr(grant_mod, "UserRepository", lambda session: Repo())
    request = OAuth2CellphoneRequest(cellphone="13800138000", verification_code=code)
    result = await CellphoneGrant(request, session=None).respond()
    assert result["token_type"] == "bearer"
    assert created["cellphone"] == "13800138000"


async def test_password_grant_rejects_wrong_password(monkeypatch):
    from app.exceptions import AuthenticationError
    from app.services.auth.grant import PasswordGrant
    from app.services.auth.oauth2_schema import OAuth2PasswordRequest

    class Repo(FakeUserRepo):
        async def get_by_username(self, username):
            from tests.unit.test_repositories import make_user

            return make_user(password=hashing.get_password_hash("right-pass"))

    import app.services.auth.grant as grant_mod

    monkeypatch.setattr(grant_mod, "UserRepository", lambda session: Repo())
    request = OAuth2PasswordRequest(username="alice", password="wrong-pass")
    with pytest.raises(AuthenticationError):
        await PasswordGrant(request, session=None).respond()
