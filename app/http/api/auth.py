import logging

from fastapi import APIRouter

from app.schemas.auth import Token
from app.services.auth.grant import PasswordGrant, CellphoneGrant
from app.services.auth.oauth2_schema import OAuth2PasswordRequest, OAuth2CellphoneRequest

router = APIRouter(
    prefix="/auth"
)


@router.post("/token", response_model=Token)
async def token(request_data: OAuth2PasswordRequest):
    """
    用户名+密码登录
    """
    grant = PasswordGrant(request_data)
    return grant.respond()


@router.post("/cellphone/token", response_model=Token)
async def cellphone_token(request_data: OAuth2CellphoneRequest):
    """
    手机号+验证码登录
    """
    grant = CellphoneGrant(request_data)
    return grant.respond()
