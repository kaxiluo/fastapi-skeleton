"""
Pydantic 数据模型
"""

from app.schemas.auth import Token
from app.schemas.user import UserBase, UserDetail

__all__ = [
    "Token",
    "UserBase",
    "UserDetail",
]
