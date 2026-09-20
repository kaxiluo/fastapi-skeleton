from app.core import redis as core_redis
from app.utils.helper import numeric_random
from config.auth import get_auth_settings
from config.settings import get_app_settings

_DEBUG_CODE_ENVS = {"local", "testing"}


# 通过 core_redis.get_redis_client() 模块属性调用（而非 from-import 直接绑定），
# 使测试可 monkeypatch app.core.redis.get_redis_client 生效


def _redis_key(cellphone: str) -> str:
    return f"verification:cellphone:{cellphone}"


async def make(cellphone: str) -> str:
    ttl = get_auth_settings().verification_code_ttl
    code = numeric_random(6)
    await core_redis.get_redis_client().set(_redis_key(cellphone), code, ex=ttl)
    return code


async def check(cellphone: str, verification_code: str) -> bool:
    debug_code = get_auth_settings().debug_verification_code
    if (
        get_app_settings().env in _DEBUG_CODE_ENVS
        and debug_code
        and verification_code == debug_code
    ):
        return True

    key = _redis_key(cellphone)
    code = await core_redis.get_redis_client().get(key)
    passed = code is not None and code == verification_code
    if passed:
        await core_redis.get_redis_client().delete(key)
    return passed
