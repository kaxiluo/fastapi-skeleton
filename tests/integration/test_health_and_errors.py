import pytest

pytestmark = pytest.mark.integration

PREFIX = "/api/v1"


async def test_health_live_no_infra(client):
    resp = await client.get(f"{PREFIX}/health/live")
    assert resp.status_code == 200


async def test_health_ready(client):
    resp = await client.get(f"{PREFIX}/health/ready")
    assert resp.status_code == 200


async def test_404_error_contract(client):
    resp = await client.get(f"{PREFIX}/no-such-route")
    assert resp.status_code == 404
    body = resp.json()
    assert set(body) == {"type", "title", "detail"}
    assert body["type"] == "http_error"


async def test_demo_db_test_commits_via_dependency(client, auth_headers):
    """验证 get_db_session 的入口层 commit 生效（创建可被后续查询看到）"""
    resp = await client.get(f"{PREFIX}/demo/db_test", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"].startswith("fake_user_by_db_test_")


async def test_demo_write_requires_token(client):
    resp = await client.get(f"{PREFIX}/demo/db_test")
    assert resp.status_code == 401
