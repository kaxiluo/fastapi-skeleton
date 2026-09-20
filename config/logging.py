from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_", env_file=".env", extra="ignore")

    level: str = "INFO"
    format: Literal["json", "console"] = "console"
    file_enable: bool = False
    retention_days: int = 0  # 轮转备份保留天数；0 = 永不删除（注意磁盘占用）


@lru_cache
def get_logging_settings() -> LoggingSettings:
    return LoggingSettings()
