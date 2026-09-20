from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.http import deps
from app.http.deps import get_db_session, get_redis
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserDetail
from app.services.auth.hashing import get_password_hash_async
from app.utils.helper import alphanumeric_random

router = APIRouter(prefix="/demo")


@router.get("/")
async def index():
    return {"message": "demo index"}


@router.get("/db_test", response_model=UserDetail)
async def db_test(
    session: AsyncSession = Depends(get_db_session),
    auth_user: User = Depends(deps.get_auth_user),
):
    username = "fake_user_by_db_test_" + alphanumeric_random(8)
    user = await UserRepository(session).create(
        username=username,
        password=await get_password_hash_async("123456"),
        nickname=username,
    )
    return user


@router.get("/redis_test")
async def redis_test(
    redis=Depends(get_redis),
    auth_user: User = Depends(deps.get_auth_user),
):
    await redis.incr("fastapi:test")
    return {"value": await redis.get("fastapi:test")}


@router.get("/{demo_id}")
async def show(demo_id: str):
    return {"demo_id": demo_id}
