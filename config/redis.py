from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 6379
    db: int = 0
    password: SecretStr = SecretStr("")


@lru_cache
def get_redis_settings() -> RedisSettings:
    return RedisSettings()
