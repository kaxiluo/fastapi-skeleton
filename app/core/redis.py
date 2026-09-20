import redis.asyncio as aioredis

from config.redis import get_redis_settings

_client: aioredis.Redis | None = None


def get_redis_client() -> aioredis.Redis:
    if _client is None:
        raise RuntimeError("Redis client not initialized; call init_redis() first")
    return _client


async def init_redis() -> None:
    global _client
    settings = get_redis_settings()
    password = settings.password.get_secret_value()
    _client = aioredis.from_url(
        f"redis://{settings.host}:{settings.port}/{settings.db}",
        password=password or None,
        decode_responses=True,
    )


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
    _client = None
