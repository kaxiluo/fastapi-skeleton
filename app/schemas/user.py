from datetime import datetime

from app.schemas.base import BaseSchema


class UserDetail(BaseSchema):
    id: int
    username: str
    nickname: str | None = None
    gender: str
    avatar: str | None = None
    cellphone: str | None = None
    email: str | None = None
    email_verified_at: datetime | None = None
    state: str
    created_at: datetime
    updated_at: datetime
