from app.models.base import Base
from app.models.user import User


def test_users_table_columns():
    cols = User.__table__.columns
    assert set(cols.keys()) == {
        "id",
        "username",
        "password",
        "cellphone",
        "email",
        "email_verified_at",
        "state",
        "nickname",
        "gender",
        "avatar",
        "created_at",
        "updated_at",
    }
    assert cols["username"].nullable is False
    assert cols["cellphone"].nullable is True
    assert cols["state"].server_default.arg == "enabled"


def test_timestamps_use_mysql_native():
    cols = User.__table__.columns
    assert cols["created_at"].server_default.arg.text == "CURRENT_TIMESTAMP"
    assert "ON UPDATE CURRENT_TIMESTAMP" in cols["updated_at"].server_default.arg.text


def test_naming_convention_applied():
    convention = Base.metadata.naming_convention
    assert convention["uq"] == "uq_%(table_name)s_%(column_0_name)s"
    ix = [i.name for i in User.__table__.indexes]
    assert "ix_users_username" in ix
    assert "ix_users_cellphone" in ix
    assert "ix_users_email" in ix


def test_user_is_enabled():
    u = User(state="enabled")
    assert u.is_enabled()
    u = User(state="disabled")
    assert not u.is_enabled()
