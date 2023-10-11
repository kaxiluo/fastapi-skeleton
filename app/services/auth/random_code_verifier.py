from app.providers.database import redis_client
from app.support.helper import numeric_random
from config.config import settings


def make(cellphone, expired=180, length=6) -> str:
    """
    生成随机码，存储到服务端，返回随机码
    """
    code = numeric_random(length)
    redis_client.setex(_get_redis_key(cellphone), expired, code)
    return code


def check(cellphone, verification_code) -> bool:
    """
    检查验证码
    """
    # 测试环境和本地环境，可以任意账号使用超级验证码
    super_code = '747380'
    if (settings.ENV == 'local' or settings.ENV == 'testing') and verification_code == super_code:
        return True

    # 校验验证码
    key = _get_redis_key(cellphone)
    code = redis_client.get(key)
    passed = code and code == verification_code
    # 若通过验证立即删除
    if passed:
        redis_client.delete(key)
    return passed


def _get_redis_key(cellphone):
    return 'verification:cellphone:' + cellphone
