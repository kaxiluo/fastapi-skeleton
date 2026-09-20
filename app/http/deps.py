from collections.abc import AsyncGenerator

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session_factory
from app.core.redis import get_redis_client
from app.exceptions import AuthenticationError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth import jwt_helper
from config.settings import API_V1_PREFIX

_oauth2_token_schema = OAuth2PasswordBearer(tokenUrl=f"{API_V1_PREFIX}/auth/token")


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_redis() -> Redis:
    return get_redis_client()


async def get_auth_user(
    token: str = Depends(_oauth2_token_schema),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    try:
        payload = jwt_helper.get_payload_by_token(token)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError(detail="Token expired") from None
    except jwt.InvalidTokenError:
        raise AuthenticationError(detail="Could not validate credentials") from None

    user_id = payload.get("sub")
    if not user_id or not str(user_id).isdigit():
        raise AuthenticationError(detail="Invalid token payload")

    user = await UserRepository(session).get(int(user_id))
    if not user:
        raise AuthenticationError(detail="User not found")
    if not user.is_enabled():
        raise AuthenticationError(detail="Inactive user")
    return user
