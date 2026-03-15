"""
异步依赖注入 - 使用 SQLAlchemy 2.0 (异步)
"""

from typing import AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exception import AuthenticationError
from app.models.user import User
from app.providers.database import database_manager
from app.services.auth import jwt_helper
from jose import jwt

oauth2_token_schema = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token"
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话（异步）

    用法:
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with database_manager.get_session() as session:
        yield session


async def get_auth_user(
    token: str = Depends(oauth2_token_schema),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    """
    获取认证用户（异步）

    从 JWT token 中解析用户 ID，并从数据库中查询用户信息

    Args:
        token: JWT token
        session: 数据库会话

    Returns:
        User: 认证用户对象

    Raises:
        AuthenticationError: token 无效或用户不存在/未激活
    """
    try:
        payload = jwt_helper.get_payload_by_token(token)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError(message="Token Expired")
    except (jwt.JWTError, jwt.JWTClaimsError):
        raise AuthenticationError(message="Could not validate credentials")

    user_id = payload.get('sub')
    if not user_id:
        raise AuthenticationError(message="Invalid token payload")

    user = await User.get_by_id(session, int(user_id))

    if not user:
        raise AuthenticationError(message="User not found")
    if not user.is_enabled():
        raise AuthenticationError(message='Inactive user')
    return user
