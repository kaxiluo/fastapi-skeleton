from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class UserBase(BaseModel):
    id: int
    username: str
    nickname: str
    gender: str
    avatar: str


class UserDetail(UserBase):
    cellphone: Optional[str] = None
    email: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    state: str
    created_at: datetime
