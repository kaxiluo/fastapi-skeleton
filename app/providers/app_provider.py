"""
应用提供者 - 异步版本
"""

from fastapi.middleware.cors import CORSMiddleware

from app.providers.database import database_manager
from app.utils.timezone_utils import setup_timezone, get_timezone
from config.config import settings


async def register(app):
    """
    注册应用配置和中间件

    Args:
        app: FastAPI 应用实例
    """
    app.debug = settings.debug
    app.title = settings.name

    # 设置应用时区
    setup_timezone()
    app.timezone = get_timezone()

    add_global_middleware(app)
    register_lifecycle_events(app)


def add_global_middleware(app):
    """
    注册全局中间件
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_lifecycle_events(app):
    """
    注册生命周期事件

    包括:
    - startup: 初始化数据库和 Redis 连接
    - shutdown: 关闭数据库和 Redis 连接
    """

    @app.on_event("startup")
    async def startup():
        """应用启动时的初始化操作"""
        # 初始化数据库连接
        await database_manager.init_db()
        print("Database initialized")

        # 初始化 Redis 连接
        await database_manager.init_redis()
        print("Redis initialized")

    @app.on_event("shutdown")
    async def shutdown():
        """应用关闭时的清理操作"""
        try:
            # 临时提升 SQLAlchemy 日志级别，避免显示连接清理错误
            import logging
            sqlalchemy_logger = logging.getLogger('sqlalchemy.pool.impl.AsyncAdaptedQueuePool')
            original_level = sqlalchemy_logger.level
            sqlalchemy_logger.setLevel(logging.CRITICAL + 1)

            try:
                await database_manager.close_db()
                await database_manager.close_redis()
            finally:
                # 恢复日志级别
                if original_level is not None:
                    sqlalchemy_logger.setLevel(original_level)
        except Exception as e:
            # 忽略关闭时的异常，避免程序退出时的错误
            print(f"Warning: Error during shutdown: {e}")
