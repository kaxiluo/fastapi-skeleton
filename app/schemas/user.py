from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer

from app.support.helper import format_datetime


# Shared properties
class UserBase(BaseModel):
    id: int
    username: str
    nickname: str
    gender: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class UserDetail(UserBase):
    cellphone: Optional[str] = None
    email: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    state: str
    created_at: datetime

    # serializers
    @field_serializer('email_verified_at', when_used='json')
    def serialize_email_verified_at(self, value: Optional[datetime]):
        return format_datetime(value)

    @field_serializer('created_at', when_used='json')
    def serialize_created_at(self, value: datetime):
        return format_datetime(value)
