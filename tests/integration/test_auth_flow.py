import pytest

from app.core.redis import get_redis_client

pytestmark = pytest.mark.integration

PREFIX = "/api/v1"


async def test_password_grant_success(client):
    resp = await client.post(
        f"{PREFIX}/auth/token",
        json={"username": "fake_user1", "password": "123456"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0
    assert body["access_token"]


async def test_password_grant_wrong_password(client):
    resp = await client.post(
        f"{PREFIX}/auth/token",
        json={"username": "fake_user1", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["type"] == "unauthorized"


async def test_cellphone_grant_full_flow_with_autoregister(client):
    cellphone = "13900139000"
    send = await client.post(
        f"{PREFIX}/auth/cellphone/verification_code", json={"cellphone": cellphone}
    )
    assert send.status_code == 200

    code = await get_redis_client().get(f"verification:cellphone:{cellphone}")
    assert code is not None

    resp = await client.post(
        f"{PREFIX}/auth/cellphone/token",
        json={"cellphone": cellphone, "verification_code": code},
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_cellphone_grant_wrong_code_rejected(client):
    cellphone = "13900139001"
    await client.post(f"{PREFIX}/auth/cellphone/verification_code", json={"cellphone": cellphone})
    resp = await client.post(
        f"{PREFIX}/auth/cellphone/token",
        json={"cellphone": cellphone, "verification_code": "000000"},
    )
    assert resp.status_code == 401
    assert resp.json() == {
        "type": "unauthorized",
        "title": "Unauthorized",
        "detail": "Incorrect verification code",
    }


async def test_send_code_rate_limited(client):
    cellphone = "13900139002"
    first = await client.post(
        f"{PREFIX}/auth/cellphone/verification_code", json={"cellphone": cellphone}
    )
    assert first.status_code == 200
    second = await client.post(
        f"{PREFIX}/auth/cellphone/verification_code", json={"cellphone": cellphone}
    )
    assert second.status_code == 400
    assert second.json()["type"] == "business_error"


async def test_send_code_invalid_cellphone(client):
    resp = await client.post(
        f"{PREFIX}/auth/cellphone/verification_code", json={"cellphone": "12345"}
    )
    assert resp.status_code == 422
    assert resp.json()["type"] == "validation_error"


async def test_verify_attempts_locked_after_failures(client):
    """验证码校验失败次数达上限后锁定，即使验证码正确也拒绝"""
    cellphone = "13900139004"
    await client.post(f"{PREFIX}/auth/cellphone/verification_code", json={"cellphone": cellphone})
    code = await get_redis_client().get(f"verification:cellphone:{cellphone}")

    for _ in range(5):
        resp = await client.post(
            f"{PREFIX}/auth/cellphone/token",
            json={"cellphone": cellphone, "verification_code": "000000"},
        )
        assert resp.status_code == 401

    resp = await client.post(
        f"{PREFIX}/auth/cellphone/token",
        json={"cellphone": cellphone, "verification_code": code},
    )
    assert resp.status_code == 400
    assert resp.json()["type"] == "business_error"


async def test_debug_code_works_in_testing_env(client):
    # .env.test 设 APP_ENV=testing 且配置了 debug code（读配置避免三处硬编码耦合）
    from config.auth import get_auth_settings

    debug_code = get_auth_settings().debug_verification_code
    resp = await client.post(
        f"{PREFIX}/auth/cellphone/token",
        json={"cellphone": "13900139003", "verification_code": debug_code},
    )
    assert resp.status_code == 200
