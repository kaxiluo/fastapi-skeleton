"""
用户模型 - 使用 SQLModel + SQLAlchemy 2.0 (异步)
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, select
from sqlalchemy import Column, String

from app.models.base_model import BaseTable


class User(BaseTable, table=True):
    """用户表模型"""

    __tablename__ = "users"

    username: str = Field(max_length=50, unique=True, index=True, description="用户名")
    password: str = Field(max_length=255, description="密码（哈希）")
    cellphone: Optional[str] = Field(max_length=20, unique=True, default=None, index=True, description="手机号")
    email: Optional[str] = Field(max_length=100, unique=True, default=None, index=True, description="邮箱")
    email_verified_at: Optional[datetime] = Field(default=None, description="邮箱验证时间")
    state: str = Field(max_length=20, default="enabled", description="状态：enabled/disabled")
    nickname: Optional[str] = Field(max_length=50, default=None, description="昵称")
    gender: str = Field(max_length=20, default="unknown", description="性别：male/female/unknown")
    avatar: Optional[str] = Field(max_length=255, default=None, description="头像URL")

    @classmethod
    async def get_or_none(cls, session, **kwargs):
        """
        异步查询单条记录

        用法:
            user = await User.get_or_none(session, id=1)
            user = await User.get_or_none(session, username="test")
        """
        statement = select(cls).where(*(getattr(cls, k) == v for k, v in kwargs.items()))
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, session, user_id: int):
        """根据 ID 查询用户"""
        statement = select(cls).where(cls.id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, session, **kwargs):
        """
        异步创建记录

        用法:
            user = await User.create(session, username="test", password="hash")
        """
        db_obj = cls(**kwargs)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @classmethod
    async def get_by_cellphone(cls, session, cellphone: str):
        """根据手机号查询用户"""
        statement = select(cls).where(cls.cellphone == cellphone)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_username(cls, session, username: str):
        """根据用户名查询用户"""
        statement = select(cls).where(cls.username == username)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    def is_enabled(self) -> bool:
        """检查用户是否启用"""
        return self.state == 'enabled'

    def to_dict(self) -> dict:
        """转换为字典（排除敏感字段）"""
        return {
            "id": self.id,
            "username": self.username,
            "cellphone": self.cellphone,
            "email": self.email,
            "email_verified_at": self.email_verified_at,
            "state": self.state,
            "nickname": self.nickname,
            "gender": self.gender,
            "avatar": self.avatar,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
