"""
用户路由 - 异步版本
"""

from fastapi import APIRouter, Depends

from app.http import deps
from app.models.user import User
from app.schemas.user import UserDetail

router = APIRouter(
    prefix="/users"
)


@router.get("/me", response_model=UserDetail)
async def me(auth_user: User = Depends(deps.get_auth_user)):
    """
    当前登录用户信息（异步）
    """
    return auth_user
