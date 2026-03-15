"""
数据库配置类
"""

from app.utils.config_loader import get_section


class DatabaseSettings:
    """数据库配置类，从 YAML 配置文件加载"""

    def __init__(self):
        self._config = get_section('database')

    @property
    def db_host(self) -> str:
        return self._config.get('host', '127.0.0.1')

    @property
    def db_port(self) -> int:
        return self._config.get('port', 3306)

    @property
    def db_database(self) -> str:
        return self._config.get('database', 'fastapi')

    @property
    def db_user(self) -> str:
        return self._config.get('user', 'root')

    @property
    def db_password(self) -> str:
        return self._config.get('password', '123456')

    @property
    def enable_sql_logging(self) -> bool:
        return self._config.get('enable_sql_logging', False)

    @property
    def sql_log_level(self) -> str:
        return self._config.get('sql_log_level', 'INFO')


class RedisSettings:
    """Redis 配置类，从 YAML 配置文件加载"""

    def __init__(self):
        self._config = get_section('redis')

    @property
    def redis_host(self) -> str:
        return self._config.get('host', 'localhost')

    @property
    def redis_port(self) -> int:
        return self._config.get('port', 6379)

    @property
    def redis_db(self) -> int:
        return self._config.get('db', 0)

    @property
    def redis_password(self) -> str:
        return self._config.get('password', '')


settings = DatabaseSettings()
redis_settings = RedisSettings()
