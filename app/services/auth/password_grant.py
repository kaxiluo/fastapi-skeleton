from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

from app.exceptions.exception import AuthenticationError
from app.models.user import User
from app.services.auth import security
from config.auth import settings


def respond_to_access_token_request(form_data: OAuth2PasswordRequestForm):
    user = User.get(User.username == form_data.username)
    if not user:
        raise AuthenticationError(message='Incorrect email or password')

    if not (user.password and security.verify_password(form_data.password, user.password)):
        raise AuthenticationError(message='Incorrect email or password')

    # 用户被禁用
    if not user.is_enabled():
        raise AuthenticationError(message='Inactive user')

    expires_delta = timedelta(minutes=settings.JWT_TTL)
    expires_in = int(expires_delta.total_seconds())
    token = security.create_access_token(user.id, expires_delta)
    return {
        "token_type": "bearer",
        "expires_in": expires_in,
        "access_token": token,
    }
