import logging

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.services.auth import password_grant

router = APIRouter(
    prefix="/auth"
)


@router.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return password_grant.respond_to_access_token_request(form_data)
