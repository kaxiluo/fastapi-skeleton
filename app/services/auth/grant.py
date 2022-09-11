from datetime import timedelta

from app.exceptions.exception import AuthenticationError
from app.models.user import User
from app.services.auth import jwt_helper, hashing, random_code_verifier
from app.services.auth.oauth2_schema import OAuth2CellphoneRequest, OAuth2PasswordRequest
from app.support.helper import alphanumeric_random
from config.auth import settings


def create_token_response_from_user(user):
    expires_delta = timedelta(minutes=settings.JWT_TTL)
    expires_in = int(expires_delta.total_seconds())
    token = jwt_helper.create_access_token(user.id, expires_delta)

    return {
        "token_type": "bearer",
        "expires_in": expires_in,
        "access_token": token,
    }


class PasswordGrant:
    def __init__(self, request_data: OAuth2PasswordRequest):
        self.request_data = request_data

    def respond(self):
        user = User.get_or_none(User.username == self.request_data.username)
        if not user:
            raise AuthenticationError(message='Incorrect email or password')

        # 用户密码校验
        if not (user.password and hashing.verify_password(self.request_data.password, user.password)):
            raise AuthenticationError(message='Incorrect email or password')

        # 用户状态校验
        if not user.is_enabled():
            raise AuthenticationError(message='Inactive user')

        return create_token_response_from_user(user)


class CellphoneGrant:
    def __init__(self, request_data: OAuth2CellphoneRequest):
        self.request_data = request_data

    def respond(self):
        cellphone = self.request_data.cellphone
        code = self.request_data.verification_code
        if not random_code_verifier.check(cellphone, code):
            raise AuthenticationError(message='Incorrect verification code')

        user = User.get_or_none(User.cellphone == cellphone)
        # 验证通过，用户不存在则创建
        if not user:
            username = 'srcp_' + alphanumeric_random()
            password = hashing.get_password_hash(alphanumeric_random())
            user = User.create(cellphone=cellphone, username=username, password=password)

        # 用户状态校验
        if not user.is_enabled():
            raise AuthenticationError(message='Inactive user')

        return create_token_response_from_user(user)
