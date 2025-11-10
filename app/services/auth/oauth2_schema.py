from typing import Optional, Literal

from pydantic import BaseModel, Field


class OAuth2PasswordRequest(BaseModel):
    """
    参照 fastapi.security.OAuth2PasswordRequestForm，把请求体从form改为json格式
    """
    grant_type: Literal["password"] = "password"
    username: str
    password: str
    scope: str = ''
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class OAuth2CellphoneRequest(BaseModel):
    grant_type: Literal["cellphone"] = "cellphone"
    cellphone: str
    verification_code: str
    scope: str = ''
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
