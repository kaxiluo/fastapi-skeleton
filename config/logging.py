"""
日志配置类
"""

from app.utils.config_loader import get_section


class Settings:
    """日志配置类，从 YAML 配置文件加载"""

    def __init__(self):
        self._config = get_section('logging')

    @property
    def log_level(self) -> str:
        return self._config.get('level', 'INFO')

    @property
    def log_retention_days(self) -> int:
        return self._config.get('retention_days', 0)


settings = Settings()
