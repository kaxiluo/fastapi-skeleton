from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AuthenticationError
from app.repositories.user_repository import UserRepository
from app.services.auth import hashing, jwt_helper, random_code_verifier, rate_limiter
from app.services.auth.oauth2_schema import (
    OAuth2CellphoneRequest,
    OAuth2PasswordRequest,
)
from app.utils.helper import alphanumeric_random
from config.auth import get_auth_settings


def create_token_response_from_user(user) -> dict:
    expires_delta = timedelta(minutes=get_auth_settings().jwt_ttl)
    token = jwt_helper.create_access_token(user.id, expires_delta)
    return {
        "token_type": "bearer",
        "expires_in": int(expires_delta.total_seconds()),
        "access_token": token,
    }


class PasswordGrant:
    def __init__(self, request_data: OAuth2PasswordRequest, session: AsyncSession):
        self.request_data = request_data
        self.repo = UserRepository(session)

    async def respond(self) -> dict:
        user = await self.repo.get_by_username(self.request_data.username)
        if not user or not user.password:
            raise AuthenticationError(detail="Incorrect username or password")
        if not await hashing.verify_password_async(self.request_data.password, user.password):
            raise AuthenticationError(detail="Incorrect username or password")
        if not user.is_enabled():
            raise AuthenticationError(detail="Inactive user")
        return create_token_response_from_user(user)


class CellphoneGrant:
    def __init__(self, request_data: OAuth2CellphoneRequest, session: AsyncSession):
        self.request_data = request_data
        self.repo = UserRepository(session)

    async def respond(self) -> dict:
        cellphone = self.request_data.cellphone
        await rate_limiter.ensure_can_verify(cellphone)
        if not await random_code_verifier.check(cellphone, self.request_data.verification_code):
            await rate_limiter.record_verify_failure(cellphone)
            raise AuthenticationError(detail="Incorrect verification code")
        await rate_limiter.clear_verify_failures(cellphone)

        user = await self.repo.get_by_cellphone(cellphone)
        if not user:
            username = "srcp_" + alphanumeric_random()
            user = await self.repo.create(
                cellphone=cellphone,
                username=username,
                password=await hashing.get_password_hash_async(alphanumeric_random()),
                nickname=username,
                gender="unknown",
            )
        if not user.is_enabled():
            raise AuthenticationError(detail="Inactive user")
        return create_token_response_from_user(user)
