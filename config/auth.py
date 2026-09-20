from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 结构性常量：算法与数量策略，变更应走代码评审
JWT_ALGORITHM = "HS256"
JWT_SECRET_MIN_BYTES = 32
SEND_CODE_DAILY_LIMIT = 10
VERIFY_MAX_ATTEMPTS = 5


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=".env", extra="ignore")

    jwt_secret: SecretStr
    # 万能验证码：仅 local/testing 生效；production 非空会被启动安全门拒绝
    debug_verification_code: str = "747380"
    jwt_ttl: int = 1440  # 分钟
    verification_code_ttl: int = 180  # 秒
    send_code_interval_seconds: int = 60
    verify_lock_seconds: int = 900

    @field_validator("jwt_secret")
    @classmethod
    def _check_secret_length(cls, value: SecretStr) -> SecretStr:
        # HS256 密钥长度是算法结构约束；PyJWT 对短密钥只发运行时警告，这里前置为启动失败
        if len(value.get_secret_value()) < JWT_SECRET_MIN_BYTES:
            raise ValueError(f"AUTH_JWT_SECRET must be at least {JWT_SECRET_MIN_BYTES} bytes")
        return value


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()
