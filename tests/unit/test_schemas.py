from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.schemas.auth import ErrorResponse, Token
from app.schemas.user import UserDetail


def make_detail() -> UserDetail:
    return UserDetail(
        id=1,
        username="alice",
        nickname=None,
        gender="unknown",
        avatar=None,
        cellphone="13800138000",
        email=None,
        email_verified_at=None,
        state="enabled",
        created_at=datetime(2026, 9, 20, 1, 30, 0, tzinfo=UTC),
        updated_at=datetime(2026, 9, 20, 1, 30, 0, tzinfo=UTC),
    )


def test_datetime_serialized_in_configured_timezone():
    detail = make_detail()
    data = detail.model_dump(mode="json")
    assert data["created_at"] == "2026-09-20 09:30:00"  # UTC+8 (Asia/Shanghai)


def test_user_detail_from_attributes():
    class FakeUser:
        id = 7
        username = "bob"
        nickname = None
        gender = "unknown"
        avatar = None
        cellphone = None
        email = None
        email_verified_at = None
        state = "enabled"
        created_at = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Shanghai"))
        updated_at = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Shanghai"))

    detail = UserDetail.model_validate(FakeUser(), from_attributes=True)
    assert detail.id == 7


def test_token_schema():
    t = Token(token_type="bearer", expires_in=86400, access_token="jwt")
    assert t.model_dump()["access_token"] == "jwt"


def test_error_response_schema():
    e = ErrorResponse(type="not_found", title="Not Found", detail="user 42")
    assert e.model_dump() == {"type": "not_found", "title": "Not Found", "detail": "user 42"}
