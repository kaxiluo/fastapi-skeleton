"""
数据库模型基类 - 使用 SQLModel + SQLAlchemy 2.0 (异步)
"""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, func

# 设置时区
TZ = ZoneInfo("Asia/Shanghai")


def now_with_timezone():
    """获取带时区的当前时间"""
    return datetime.now(TZ)


class BaseTable(SQLModel):
    """数据库表基类 - 所有数据库表的基类"""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=now_with_timezone,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=now_with_timezone,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
        description="更新时间"
    )


class BaseModel(SQLModel):
    """响应模型基类 - 用于 API 响应"""

    id: int
    created_at: datetime
    updated_at: datetime


class BaseModelWithSoftDelete(BaseTable):
    """支持软删除的模型基类"""

    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="删除时间（软删除）"
    )
