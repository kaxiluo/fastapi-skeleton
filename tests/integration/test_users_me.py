import pytest

pytestmark = pytest.mark.integration

PREFIX = "/api/v1"


async def test_me_requires_token(client):
    # 无 token：OAuth2 schema 抛 HTTPException，渲染为 http_error，但仍是 401 + Bearer challenge
    resp = await client.get(f"{PREFIX}/users/me")
    assert resp.status_code == 401
    assert resp.json()["type"] == "http_error"
    assert resp.headers.get("www-authenticate") == "Bearer"


async def test_me_invalid_token(client):
    # 无效 token：get_auth_user 抛 AuthenticationError，渲染为 unauthorized
    resp = await client.get(f"{PREFIX}/users/me", headers={"Authorization": "Bearer bad-token"})
    assert resp.status_code == 401
    assert resp.json()["type"] == "unauthorized"


async def test_me_expired_token(client):
    from datetime import timedelta

    from app.services.auth.jwt_helper import create_access_token

    token = create_access_token(1, timedelta(seconds=-10))
    resp = await client.get(f"{PREFIX}/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["type"] == "unauthorized"
    assert resp.json()["detail"] == "Token expired"


async def test_me_with_token(client, auth_headers):
    resp = await client.get(f"{PREFIX}/users/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "integration_authed"
    assert body["created_at"]  # 时区格式化后的字符串
