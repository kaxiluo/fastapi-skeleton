"""
异步数据库和Redis连接管理
"""

import logging
from typing import Optional
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import SQLModel
from config.database import settings as db_settings, redis_settings
from config.config import settings as app_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy 声明性基类"""
    pass


class DatabaseManager:
    """异步数据库和Redis管理器"""

    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._engine = None
        self._session_factory = None

    @property
    def database_url(self) -> str:
        """构建数据库连接URL"""
        return (
            f"mysql+aiomysql://{db_settings.db_user}:{db_settings.db_password}@"
            f"{db_settings.db_host}:{db_settings.db_port}/{db_settings.db_database}"
            f"?charset=utf8mb4"
        )

    @property
    async def redis(self) -> aioredis.Redis:
        """获取异步 Redis 客户端（懒加载）"""
        if self._redis is None:
            self._redis = await aioredis.from_url(
                f"redis://{redis_settings.redis_host}:{redis_settings.redis_port}/{redis_settings.redis_db}",
                password=redis_settings.redis_password or None,
                decode_responses=True
            )
        return self._redis

    async def close_redis(self):
        """关闭 Redis 连接"""
        if self._redis:
            try:
                await self._redis.close()
                self._redis = None
            except Exception as e:
                # 静默忽略关闭时的连接错误（这些是正常的）
                pass

    async def init_redis(self):
        """初始化 Redis 连接"""
        await self.redis  # 触发懒加载

    async def init_db(self):
        """初始化数据库连接"""
        self._engine = create_async_engine(
            self.database_url,
            echo=False,  # 可以通过配置控制
            future=True,
            # 禁用SQLAlchemy自带的日志，使用项目统一的日志配置
            echo_pool=False,
            # 连接池配置 - 解决MySQL连接断开问题
            pool_size=10,          # 连接池大小
            max_overflow=20,       # 超出连接池大小的最大连接数
            pool_recycle=3600,     # 连接回收时间（1小时），防止MySQL断开连接
            pool_pre_ping=True,    # 连接前ping检查，确保连接有效
            pool_timeout=30,       # 获取连接超时时间
            connect_args={
                "connect_timeout": 60,    # 连接超时
                "charset": "utf8mb4",     # 字符集
                "autocommit": False,      # 手动提交
                "init_command": "SET time_zone = '+08:00'",  # 设置MySQL时区
            }
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @asynccontextmanager
    async def get_session(self):
        """获取数据库会话"""
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close_db(self):
        """关闭数据库连接"""
        if self._engine:
            try:
                # 先关闭异步引擎
                await self._engine.dispose()
            except Exception:
                # 静默处理异步关闭异常
                pass

            try:
                # 再关闭同步引擎（如果存在）
                if hasattr(self._engine, 'sync_engine'):
                    self._engine.sync_engine.dispose()
            except Exception:
                # 静默处理同步关闭异常
                pass


# 全局数据库管理器实例
database_manager = DatabaseManager()
