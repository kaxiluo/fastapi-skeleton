from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from config.auth import JWT_ALGORITHM, get_auth_settings


def create_access_token(subject: Any, expires_delta: timedelta | None = None) -> str:
    settings = get_auth_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_ttl)
    expire = datetime.now(UTC) + expires_delta
    payload = {"exp": expire, "sub": str(subject)}
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=JWT_ALGORITHM)


def get_payload_by_token(encoded_jwt: str) -> dict:
    settings = get_auth_settings()
    return jwt.decode(
        encoded_jwt,
        settings.jwt_secret.get_secret_value(),
        algorithms=[JWT_ALGORITHM],
    )
