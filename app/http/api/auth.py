from fastapi import APIRouter, Depends, Body
from starlette.responses import JSONResponse

from app.http.deps import get_db
from app.schemas.auth import Token
from app.services.auth import random_code_verifier
from app.services.auth.grant import PasswordGrant, CellphoneGrant
from app.services.auth.oauth2_schema import OAuth2PasswordRequest, OAuth2CellphoneRequest
from app.services.sms import sms_sender
from app.support.helper import is_chinese_cellphone

router = APIRouter(
    prefix="/auth"
)


@router.post("/token", response_model=Token, dependencies=[Depends(get_db)])
def token(request_data: OAuth2PasswordRequest):
    """
    用户名+密码登录
    """
    grant = PasswordGrant(request_data)
    return grant.respond()


@router.post("/cellphone/token", response_model=Token, dependencies=[Depends(get_db)])
def cellphone_token(request_data: OAuth2CellphoneRequest):
    """
    手机号+验证码登录
    """
    grant = CellphoneGrant(request_data)
    return grant.respond()


@router.post("/cellphone/verification_code")
def send_verification_code(cellphone: str = Body(..., embed=True)):
    """
    发送验证码
    """
    if not is_chinese_cellphone(cellphone):
        return JSONResponse(status_code=422, content={"message": 'invalid cellphone'})

    code = random_code_verifier.make(cellphone)
    # fake send
    sms_sender.send(cellphone, {'code': code})
    return {"success": True}
