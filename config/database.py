from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST: str = '127.0.0.1'
    PORT: int = 3306
    DATABASE: str = 'fastapi'
    USER: str = 'root'
    PASSWORD: str = '123456'

    class Config:
        env_prefix = 'DB_'
        env_file = ".env"


settings = Settings()
