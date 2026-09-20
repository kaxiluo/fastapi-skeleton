from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# 结构性常量：随代码变更，不作为环境变量暴露
CORS_ORIGINS: list[str] = ["*"]
CORS_ALLOW_CREDENTIALS = False
API_V1_PREFIX = "/api/v1"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    name: str = "FastAPI Skeleton"
    env: Literal["local", "testing", "production"] = "local"
    debug: bool = True
    timezone: str = "Asia/Shanghai"

    @property
    def is_production(self) -> bool:
        return self.env == "production"


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()


def validate_runtime_safety() -> None:
    """生产环境启动安全门：危险配置直接拒绝启动（入口层调用）"""
    from config.auth import get_auth_settings

    if not get_app_settings().is_production:
        return
    auth = get_auth_settings()
    problems = []
    if auth.debug_verification_code:
        problems.append("AUTH_DEBUG_VERIFICATION_CODE must be empty in production")
    secret = auth.jwt_secret.get_secret_value()
    if secret.startswith("change-me"):
        problems.append("AUTH_JWT_SECRET looks like a placeholder")
    if problems:
        raise RuntimeError("unsafe production config: " + "; ".join(problems))
