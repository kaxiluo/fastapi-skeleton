from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_TTL: int = 60 * 24 * 8
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = 'HS256'

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()
