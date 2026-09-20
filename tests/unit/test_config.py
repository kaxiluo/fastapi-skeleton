import pytest

from config.auth import JWT_ALGORITHM, AuthSettings
from config.database import DatabaseSettings
from config.settings import API_V1_PREFIX, CORS_ORIGINS, AppSettings

# 统一 _env_file=None：不受本机 .env 干扰，断言只依赖 monkeypatch 的环境变量


def test_app_settings_prefix_and_defaults(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Skeleton Test")
    monkeypatch.setenv("APP_ENV", "production")
    s = AppSettings(_env_file=None)
    assert s.name == "Skeleton Test"
    assert s.env == "production"
    assert s.is_production
    assert s.timezone == "Asia/Shanghai"


def test_structural_constants():
    assert API_V1_PREFIX == "/api/v1"
    assert CORS_ORIGINS == ["*"]
    assert JWT_ALGORITHM == "HS256"


def test_app_settings_rejects_invalid_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    with pytest.raises(ValueError):
        AppSettings(_env_file=None)


def test_database_settings_url(monkeypatch):
    monkeypatch.setenv("DB_HOST", "db.local")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv("DB_NAME", "fastapi")
    s = DatabaseSettings(_env_file=None)
    assert s.url == ("mysql+aiomysql://root:secret@db.local:3306/fastapi?charset=utf8mb4")
    assert s.password.get_secret_value() == "secret"


def test_database_settings_url_encodes_special_password(monkeypatch):
    monkeypatch.setenv("DB_PASSWORD", "p@ss:w/rd#1")
    s = DatabaseSettings(_env_file=None)
    assert "p%40ss%3Aw%2Frd%231@" in s.url


def test_auth_settings_requires_secret():
    import os

    saved = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("AUTH_")}
    try:
        with pytest.raises(ValueError):
            AuthSettings(_env_file=None)
    finally:
        os.environ.update(saved)


def test_auth_settings_env_override(monkeypatch):
    monkeypatch.setenv("AUTH_JWT_SECRET", "s3cret-0123456789abcdefghijklmnop")
    s = AuthSettings(_env_file=None)
    assert s.jwt_secret.get_secret_value() == "s3cret-0123456789abcdefghijklmnop"
    assert s.jwt_ttl == 1440
    assert s.verification_code_ttl == 180
    assert s.send_code_interval_seconds == 60
    assert s.verify_lock_seconds == 900


def test_auth_settings_rejects_short_secret(monkeypatch):
    monkeypatch.setenv("AUTH_JWT_SECRET", "tooshort")
    with pytest.raises(ValueError, match="32 bytes"):
        AuthSettings(_env_file=None)


def test_auth_structural_constants():
    from config.auth import JWT_ALGORITHM, SEND_CODE_DAILY_LIMIT, VERIFY_MAX_ATTEMPTS

    assert JWT_ALGORITHM == "HS256"
    assert SEND_CODE_DAILY_LIMIT == 10
    assert VERIFY_MAX_ATTEMPTS == 5


def _clear_caches():
    from config.auth import get_auth_settings
    from config.settings import get_app_settings

    get_app_settings.cache_clear()
    get_auth_settings.cache_clear()


def test_runtime_safety_rejects_debug_code_in_production(monkeypatch):
    from config.settings import validate_runtime_safety

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_JWT_SECRET", "x" * 40)
    monkeypatch.setenv("AUTH_DEBUG_VERIFICATION_CODE", "747380")
    _clear_caches()
    with pytest.raises(RuntimeError, match="AUTH_DEBUG_VERIFICATION_CODE"):
        validate_runtime_safety()
    _clear_caches()


def test_runtime_safety_rejects_placeholder_secret(monkeypatch):
    from config.settings import validate_runtime_safety

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_JWT_SECRET", "change-me-to-a-random-string-32-bytes-or-longer")
    _clear_caches()
    with pytest.raises(RuntimeError, match="placeholder"):
        validate_runtime_safety()
    _clear_caches()


def test_runtime_safety_passes_with_good_production_config(monkeypatch):
    from config.settings import validate_runtime_safety

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_JWT_SECRET", "a-proper-random-secret-32-bytes-or-more")
    monkeypatch.setenv("AUTH_DEBUG_VERIFICATION_CODE", "")  # 空串覆盖本地 .env 的回填
    _clear_caches()
    validate_runtime_safety()  # 不抛即通过
    _clear_caches()


def test_runtime_safety_skipped_outside_production(monkeypatch):
    from config.settings import validate_runtime_safety

    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("AUTH_JWT_SECRET", "x" * 40)
    monkeypatch.setenv("AUTH_DEBUG_VERIFICATION_CODE", "747380")
    _clear_caches()
    validate_runtime_safety()  # local 不检查
    _clear_caches()
