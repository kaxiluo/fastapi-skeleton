from config.config import settings


def make(cellphone, expired=180, length=6) -> str:
    """
    生成随机码，存储到服务端，返回随机码 todo
    """
    pass


def check(cellphone, verification_code) -> bool:
    """
    检查验证码
    """
    # 测试环境和本地环境，可以任意账号使用超级验证码
    super_code = '747380'
    if (settings.ENV == 'local' or settings.ENV == 'testing') and verification_code == super_code:
        return True

    # 校验验证码 todo

    return False
