import httpx
import pytest
from fastapi import FastAPI
from httpx import ASGITransport

from app.core.middleware import RequestContextMiddleware


@pytest.fixture
async def client():
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        yield c


async def test_request_id_generated(client):
    resp = await client.get("/ping")
    assert resp.status_code == 200
    assert resp.headers["X-Request-ID"]


async def test_request_id_passthrough(client):
    resp = await client.get("/ping", headers={"X-Request-ID": "fixed-id-123"})
    assert resp.headers["X-Request-ID"] == "fixed-id-123"


async def test_request_id_invalid_header_replaced(client):
    # 非法请求 ID（含空格/超长/特殊字符）不透传，改为服务端生成
    bad_ids = ["has space", "x" * 100, "abc\ndef", ""]
    for bad in bad_ids:
        resp = await client.get("/ping", headers={"X-Request-ID": bad} if bad else {})
        assert resp.headers["X-Request-ID"] != bad
        assert resp.headers["X-Request-ID"]
