"""
演示路由 - 异步版本
"""

from fastapi import APIRouter, Depends

from app.http.deps import get_db_session
from app.models.user import User
from app.providers.database import database_manager
from app.services.auth import hashing
from app.schemas.user import UserDetail
from app.utils.helper import alphanumeric_random
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/demo"
)


@router.get("/")
async def index():
    return {"message": "demo index"}


@router.get("/db_test", response_model=UserDetail)
async def db_test(session: AsyncSession = Depends(get_db_session)):
    """数据库测试（异步）"""
    password = hashing.get_password_hash("123456")
    username = 'fake_user_by_db_test_' + alphanumeric_random(8)
    user = await User.create(session, username=username, password=password, nickname=username)
    # 重新加载
    user = await User.get_by_id(session, user.id)
    return user


@router.get("/redis_test")
async def redis_test():
    """Redis 测试（异步）"""
    redis = await database_manager.redis
    value = await redis.incr('fastapi:test')
    return {'value': await redis.get('fastapi:test')}


@router.get("/{demo_id}")
async def show(demo_id: str):
    return {"demo_id": demo_id}
