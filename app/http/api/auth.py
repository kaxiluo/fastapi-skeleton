from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppValidationError
from app.http.deps import get_db_session
from app.schemas.auth import ErrorResponse, Token
from app.services.auth import random_code_verifier, rate_limiter
from app.services.auth.grant import CellphoneGrant, PasswordGrant
from app.services.auth.oauth2_schema import OAuth2CellphoneRequest, OAuth2PasswordRequest
from app.services.sms import sms_sender
from app.utils.helper import is_chinese_cellphone

router = APIRouter(prefix="/auth")


@router.post("/token", response_model=Token, responses={401: {"model": ErrorResponse}})
async def token(
    request_data: OAuth2PasswordRequest,
    session: AsyncSession = Depends(get_db_session),
):
    return await PasswordGrant(request_data, session).respond()


@router.post("/cellphone/token", response_model=Token, responses={401: {"model": ErrorResponse}})
async def cellphone_token(
    request_data: OAuth2CellphoneRequest,
    session: AsyncSession = Depends(get_db_session),
):
    return await CellphoneGrant(request_data, session).respond()


@router.post(
    "/cellphone/verification_code",
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def send_verification_code(cellphone: str = Body(..., embed=True)):
    if not is_chinese_cellphone(cellphone):
        raise AppValidationError(detail="invalid cellphone")
    await rate_limiter.ensure_can_send(cellphone)
    code = await random_code_verifier.make(cellphone)
    sms_sender.send(cellphone, {"code": code})
    return {"success": True}
