import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NAME: str = "fastapi"
    DEBUG: bool = False
    ENV: str = "production"

    BASE_PATH: str = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    URL: str = "http://localhost"
    TIME_ZONE: str = "Asia/Shanghai"

    model_config = SettingsConfigDict(
        env_prefix='APP_',
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()
