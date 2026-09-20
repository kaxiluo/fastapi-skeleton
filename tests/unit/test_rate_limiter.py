import pytest

from app.exceptions import BusinessError


@pytest.fixture(autouse=True)
def auth_secret(monkeypatch):
    from config.auth import get_auth_settings

    monkeypatch.setenv("AUTH_JWT_SECRET", "unit-test-secret-that-is-long-enough-32")
    get_auth_settings.cache_clear()
    yield
    get_auth_settings.cache_clear()


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
    def __init__(self, preset=None):
        self.counts = {}
        self.expires = {}
        self.store = {}
        self.preset = preset or {}

    def pipeline(self, transaction=True):
        return FakePipeline(self)

    async def incr(self, key):
        value = self.preset.pop(key) if key in self.preset else self.counts.get(key, 0) + 1
        self.counts[key] = value
        self.store[key] = str(value)  # get/delete 走 store
        return value

    async def expire(self, key, ttl):
        self.expires[key] = ttl
        return True

    async def get(self, key):
        return self.store.get(key)

    async def delete(self, key):
        self.store.pop(key, None)


async def test_first_send_allowed(monkeypatch):
    from app.core import redis as core_redis
    from app.services.auth import rate_limiter

    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)
    await rate_limiter.ensure_can_send("13800138000")  # 不抛即通过
    assert fake.counts["ratelimit:code:daily:13800138000"] == 1
    assert fake.expires["ratelimit:code:interval:13800138000"] == 60


async def test_interval_window_blocks_second_send(monkeypatch):
    from app.core import redis as core_redis
    from app.services.auth import rate_limiter

    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)
    await rate_limiter.ensure_can_send("13800138000")
    with pytest.raises(BusinessError, match="Please wait"):
        await rate_limiter.ensure_can_send("13800138000")


async def test_daily_limit_exceeded(monkeypatch):
    from app.core import redis as core_redis
    from app.services.auth import rate_limiter

    monkeypatch.setattr(rate_limiter, "SEND_CODE_DAILY_LIMIT", 3)
    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)
    # 预置每日计数已达上限（每次调用先 incr daily 再 incr interval）
    fake.preset["ratelimit:code:daily:13800138000"] = 4
    with pytest.raises(BusinessError, match="Daily"):
        await rate_limiter.ensure_can_send("13800138000")


async def test_verify_lockout_after_max_failures(monkeypatch):
    from app.core import redis as core_redis
    from app.services.auth import rate_limiter

    fake = FakeRedis()
    monkeypatch.setattr(core_redis, "get_redis_client", lambda: fake)

    cellphone = "13800138000"
    for _ in range(5):
        await rate_limiter.ensure_can_verify(cellphone)  # 未达上限都放行
        await rate_limiter.record_verify_failure(cellphone)
    assert fake.counts["ratelimit:verify:fail:13800138000"] == 5
    assert fake.expires["ratelimit:verify:fail:13800138000"] == 900

    with pytest.raises(BusinessError, match="Too many verification attempts"):
        await rate_limiter.ensure_can_verify(cellphone)

    await rate_limiter.clear_verify_failures(cellphone)
    await rate_limiter.ensure_can_verify(cellphone)  # 清除后恢复
