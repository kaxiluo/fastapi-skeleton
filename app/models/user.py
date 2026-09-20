from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {"mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    cellphone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime())
    state: Mapped[str] = mapped_column(String(20), server_default="enabled", default="enabled")
    nickname: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String(20), server_default="unknown", default="unknown")
    avatar: Mapped[str | None] = mapped_column(String(255))

    def is_enabled(self) -> bool:
        return self.state == "enabled"
