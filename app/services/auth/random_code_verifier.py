"""
验证码验证器 - 异步版本
"""

from app.providers.database import database_manager
from app.utils.helper import numeric_random
from config.config import settings


async def make(cellphone, expired=180, length=6) -> str:
    """
    生成随机码，存储到服务端，返回随机码（异步）

    Args:
        cellphone: 手机号
        expired: 过期时间（秒），默认 180 秒
        length: 验证码长度，默认 6 位

    Returns:
        str: 生成的验证码
    """
    code = numeric_random(length)
    redis = await database_manager.redis
    await redis.setex(_get_redis_key(cellphone), expired, code)
    return code


async def check(cellphone, verification_code) -> bool:
    """
    检查验证码（异步）

    Args:
        cellphone: 手机号
        verification_code: 验证码

    Returns:
        bool: 验证是否通过

    Note:
        调试环境和本地环境，可使用超级验证码 747380
    """
    # 调试环境和本地环境超级验证码
    super_code = '747380'
    if (settings.env == 'local' or settings.env == 'testing') and verification_code == super_code:
        return True

    # 校验验证码
    key = _get_redis_key(cellphone)
    redis = await database_manager.redis
    code = await redis.get(key)
    passed = code and code == verification_code
    # 若通过验证立即删除
    if passed:
        await redis.delete(key)
    return passed


def _get_redis_key(cellphone):
    """生成 Redis 键名"""
    return 'verification:cellphone:' + cellphone
