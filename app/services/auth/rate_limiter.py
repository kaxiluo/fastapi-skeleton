from datetime import timedelta

from app.core import redis as core_redis
from app.exceptions import BusinessError
from app.utils.timezone_utils import now
from config.auth import SEND_CODE_DAILY_LIMIT, VERIFY_MAX_ATTEMPTS, get_auth_settings

# 与 random_code_verifier 相同：经模块属性调用以便测试 monkeypatch


def _daily_key(cellphone: str) -> str:
    return f"ratelimit:code:daily:{cellphone}"


def _interval_key(cellphone: str) -> str:
    return f"ratelimit:code:interval:{cellphone}"


def _verify_fail_key(cellphone: str) -> str:
    return f"ratelimit:verify:fail:{cellphone}"


def _seconds_until_midnight() -> int:
    current = now()
    tomorrow = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, int((tomorrow - current).total_seconds()))


async def _incr_with_expire(key: str, ttl: int) -> int:
    # incr+expire 放进事务管道：避免两步之间崩溃留下无 TTL 的键导致永久限流
    redis = core_redis.get_redis_client()
    async with redis.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, ttl)
        count, _ = await pipe.execute()
    return int(count)


async def ensure_can_send(cellphone: str) -> None:
    settings = get_auth_settings()
    daily_count = await _incr_with_expire(_daily_key(cellphone), _seconds_until_midnight())
    if daily_count > SEND_CODE_DAILY_LIMIT:
        raise BusinessError(detail="Daily verification code sending limit exceeded")

    interval_count = await _incr_with_expire(
        _interval_key(cellphone), settings.send_code_interval_seconds
    )
    if interval_count > 1:
        raise BusinessError(detail="Please wait before requesting another code")


async def ensure_can_verify(cellphone: str) -> None:
    count = await core_redis.get_redis_client().get(_verify_fail_key(cellphone))
    if count is not None and int(count) >= VERIFY_MAX_ATTEMPTS:
        raise BusinessError(detail="Too many verification attempts, please try later")


async def record_verify_failure(cellphone: str) -> None:
    ttl = get_auth_settings().verify_lock_seconds
    await _incr_with_expire(_verify_fail_key(cellphone), ttl)


async def clear_verify_failures(cellphone: str) -> None:
    await core_redis.get_redis_client().delete(_verify_fail_key(cellphone))
