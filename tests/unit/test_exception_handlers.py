import httpx
import pytest
from fastapi import FastAPI
from httpx import ASGITransport

from app.exceptions.errors import (
    AppError,
    AppValidationError,
    AuthenticationError,
    BusinessError,
    NotFoundError,
)
from app.exceptions.handlers import register_exception_handlers


@pytest.fixture
async def client():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/not-found")
    async def not_found():
        raise NotFoundError(detail="user 42 not found")

    @app.get("/auth")
    async def auth_error():
        raise AuthenticationError(detail="bad token")

    @app.get("/business")
    async def business_error():
        raise BusinessError(detail="limit exceeded")

    @app.get("/validation")
    async def validation():
        raise AppValidationError(detail="invalid cellphone")

    @app.get("/http-404")
    async def http_404():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="nope")

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        yield c


async def test_app_error_shape(client):
    resp = await client.get("/not-found")
    assert resp.status_code == 404
    body = resp.json()
    assert body == {"type": "not_found", "title": "Not Found", "detail": "user 42 not found"}


async def test_authentication_error(client):
    resp = await client.get("/auth")
    assert resp.status_code == 401
    assert resp.json()["type"] == "unauthorized"


async def test_business_error(client):
    resp = await client.get("/business")
    assert resp.status_code == 400
    assert resp.json()["type"] == "business_error"


async def test_unhandled_exception_local_env_hides_nothing(monkeypatch):
    # ServerErrorMiddleware 发完 500 响应后总会 re-raise，须用 raise_app_exceptions=False
    monkeypatch.setenv("APP_ENV", "local")
    from config.settings import get_app_settings

    get_app_settings.cache_clear()

    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom():
        raise RuntimeError("secret internals")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
        resp = await client.get("/boom")
    assert resp.status_code == 500
    body = resp.json()
    assert body["type"] == "internal_error"
    assert body["detail"] == "secret internals"
    get_app_settings.cache_clear()


async def test_unhandled_exception_production_hides_detail(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    from config.settings import get_app_settings

    get_app_settings.cache_clear()

    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom():
        raise RuntimeError("secret internals")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
        resp = await client.get("/boom")
    assert resp.status_code == 500
    body = resp.json()
    assert body["type"] == "internal_error"
    assert "detail" not in body  # 生产环境不泄露内部错误
    get_app_settings.cache_clear()


async def test_starlette_http_exception_same_shape(client):
    resp = await client.get("/http-404")
    assert resp.status_code == 404
    assert resp.json()["type"] == "http_error"


async def test_request_validation_error_shape(client):
    resp = await client.get("/validation")
    assert resp.status_code == 422
    assert resp.json()["type"] == "validation_error"


async def test_fastapi_validation_aggregates_errors():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/q")
    async def q(page: int):
        return {"page": page}

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        resp = await c.get("/q", params={"page": "abc"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["type"] == "validation_error"
    assert isinstance(body["detail"], list)
    assert body["detail"][0]["loc"] == ["query", "page"]


# AppError 基类可直接实例化（status 500）
def test_app_error_base_defaults():
    e = AppError()
    assert e.status_code == 500
    assert e.detail == "Internal Server Error"
