from typing import Any

from pydantic import BaseModel

from app.schemas.base import BaseSchema


class Token(BaseModel):
    token_type: str
    expires_in: int
    access_token: str


class ErrorResponse(BaseSchema):
    type: str
    title: str
    detail: Any = None
