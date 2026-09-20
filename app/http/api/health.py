from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.http.deps import get_db_session, get_redis

router = APIRouter(prefix="/health")


@router.get("/live")
async def live():
    return {"status": "ok"}


@router.get("/ready")
async def ready(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
):
    await session.execute(text("SELECT 1"))
    await redis.ping()
    return {"status": "ok"}
