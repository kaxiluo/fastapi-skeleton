"""
应用配置类
"""

import os
from app.utils.config_loader import get_section


class Settings:
    """应用配置类，从 YAML 配置文件加载"""

    def __init__(self):
        self._config = get_section('app')
        self.BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def name(self) -> str:
        return self._config.get('name', "FastAPI Skeleton")

    @property
    def debug(self) -> bool:
        return self._config.get('debug', False)

    @property
    def env(self) -> str:
        return self._config.get('env', "production")

    @property
    def server_host(self) -> str:
        return self._config.get('server', {}).get('host', "0.0.0.0")

    @property
    def server_port(self) -> int:
        return self._config.get('server', {}).get('port', 8000)

    @property
    def timezone(self) -> str:
        return self._config.get('timezone', "Asia/Shanghai")


settings = Settings()
