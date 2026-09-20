from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    password: SecretStr = SecretStr("")
    name: str = "fastapi"
    # 高级项：默认值够用，不入 .env.example；需要时可用 DB_POOL_SIZE 等环境变量覆盖
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600

    @property
    def url(self) -> str:
        password = quote_plus(self.password.get_secret_value())
        return (
            f"mysql+aiomysql://{self.user}:{password}@{self.host}:{self.port}/{self.name}"
            "?charset=utf8mb4"
        )


@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()
