"""
辅助工具函数
"""

import re
import secrets
import string


def alphanumeric_random(length: int = 16) -> str:
    """生成指定长度的字母数字随机串（CSPRNG）"""
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


def numeric_random(length: int) -> str:
    """生成指定长度的数字随机串（CSPRNG，用于验证码等安全场景）"""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def is_chinese_cellphone(cellphone: str) -> bool:
    """判断号码是否为中国的手机号"""
    return bool(re.fullmatch(r"1\d{10}", cellphone))
