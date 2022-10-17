from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.support.helper import format_datetime


# Shared properties
class UserBase(BaseModel):
    id: int
    username: str
    nickname: str
    gender: str
    avatar: str

    class Config:
        orm_mode = True


class UserDetail(UserBase):
    cellphone: Optional[str] = None
    email: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    state: str
    created_at: datetime

    # validators
    _format_datetime_email_verified_at = validator('email_verified_at', allow_reuse=True)(format_datetime)
    _format_datetime_created_at = validator('created_at', allow_reuse=True)(format_datetime)
