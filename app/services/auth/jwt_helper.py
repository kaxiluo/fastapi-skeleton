from datetime import datetime, timedelta

from jose import jwt
from typing import Any, Union

from config.auth import settings


def create_access_token(
        subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_TTL)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def get_payload_by_token(encoded_jwt):
    return jwt.decode(encoded_jwt, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
