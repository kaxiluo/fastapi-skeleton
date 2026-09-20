from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.db import close_db, init_db
from app.core.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await init_db()
    try:
        await init_redis()
        yield
    finally:
        await close_redis()
        await close_db()
