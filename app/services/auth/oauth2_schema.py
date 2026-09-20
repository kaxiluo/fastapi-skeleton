from typing import Literal

from pydantic import BaseModel


class OAuth2PasswordRequest(BaseModel):
    """OAuth2 密码授权请求体（JSON，而非 form 表单）"""

    grant_type: Literal["password"] = "password"
    username: str
    password: str
    scope: str = ""
    client_id: str | None = None
    client_secret: str | None = None


class OAuth2CellphoneRequest(BaseModel):
    grant_type: Literal["cellphone"] = "cellphone"
    cellphone: str
    verification_code: str
    scope: str = ""
    client_id: str | None = None
    client_secret: str | None = None
