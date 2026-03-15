"""
认证配置类
"""

from app.utils.config_loader import get_section


class Settings:
    """认证配置类，从 YAML 配置文件加载"""

    def __init__(self):
        self._config = get_section('auth')

    @property
    def jwt_ttl(self) -> int:
        return self._config.get('jwt_ttl', 1440)

    @property
    def jwt_secret_key(self) -> str:
        return self._config.get('jwt_secret_key', '')

    @property
    def jwt_algorithm(self) -> str:
        return self._config.get('jwt_algorithm', 'HS256')


settings = Settings()
