"""
日志系统配置
"""

import logging
import os
import sys
import zoneinfo
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

from config.logging import settings
from app.utils.timezone_utils import get_timezone
from config.database import settings as db_settings


def configure_service_logging(service_name: str, extra_loggers: list = None):
    """配置服务日志系统

    Args:
        service_name: 服务名称，用于区分不同服务的日志文件
        extra_loggers: 需要特殊处理的额外日志器列表
    """
    from config.config import settings as app_settings

    # 创建日志目录
    base_log_dir = os.path.join(app_settings.BASE_PATH, "storage", "logs", service_name.lower())
    os.makedirs(base_log_dir, exist_ok=True)

    # 创建时区感知的日志格式化器
    class TimeZoneFormatter(logging.Formatter):
        def __init__(self, fmt=None, datefmt=None):
            super().__init__(fmt, datefmt)
            self.timezone = get_timezone()

        def formatTime(self, record, datefmt=None):
            if self.timezone:
                utc_dt = datetime.fromtimestamp(record.created, tz=zoneinfo.ZoneInfo('UTC'))
                local_dt = utc_dt.astimezone(self.timezone)
            else:
                local_dt = datetime.fromtimestamp(record.created)

            if datefmt:
                return local_dt.strftime(datefmt)
            else:
                return str(local_dt)

    formatter = TimeZoneFormatter(
        '%(asctime)s | %(levelname)-5s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.addHandler(console_handler)

    # 文件处理器（按天轮转）
    today = datetime.now(get_timezone()).strftime('%Y-%m-%d')
    actual_log_path = os.path.join(base_log_dir, f"{service_name.lower()}-{today}.log")

    file_handler = TimedRotatingFileHandler(
        actual_log_path,
        when='midnight',
        interval=1,
        backupCount=settings.log_retention_days,
        encoding='utf-8'
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.extMatch = r"^\d{4}-\d{2}-\d{2}$"
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.addHandler(file_handler)

    # 配置额外的日志器
    if extra_loggers:
        for logger_name in extra_loggers:
            logger_obj = logging.getLogger(logger_name)
            logger_obj.setLevel(getattr(logging, settings.log_level.upper()))
            logger_obj.handlers.clear()
            logger_obj.addHandler(console_handler)
            logger_obj.addHandler(file_handler)
            logger_obj.propagate = False

    # 配置 SQLAlchemy 日志器
    if db_settings.enable_sql_logging:
        sqlalchemy_loggers = [
            'sqlalchemy.engine',
            'sqlalchemy.engine.Engine',
            'sqlalchemy.dialects',
            'sqlalchemy.orm'
        ]

        for logger_name in sqlalchemy_loggers:
            sqlalchemy_logger = logging.getLogger(logger_name)
            sqlalchemy_logger.setLevel(getattr(logging, db_settings.sql_log_level.upper()))
            sqlalchemy_logger.handlers.clear()
            sqlalchemy_logger.addHandler(console_handler)
            sqlalchemy_logger.addHandler(file_handler)
            sqlalchemy_logger.propagate = False

        # 单独配置 mapper 和 pool 日志，避免大量日志
        for logger_name in ['sqlalchemy.orm.mapper', 'sqlalchemy.pool', 'sqlalchemy.pool.impl.AsyncAdaptedQueuePool']:
            logging.getLogger(logger_name).setLevel(logging.WARNING)


def configure_web_logging():
    """配置 Web 服务日志系统（包括 uvicorn）"""
    uvicorn_loggers = ["uvicorn", "uvicorn.access", "uvicorn.error", "uvicorn.asgi"]
    configure_service_logging("web", uvicorn_loggers)


def get_logger(name: str = None):
    """获取日志器实例

    Args:
        name: logger 名称

    Returns:
        logging.Logger: 日志器实例
    """
    return logging.getLogger(name)
