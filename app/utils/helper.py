"""
辅助工具函数
"""

import random
import re
import string
from datetime import datetime


def alphanumeric_random(length: int = 16) -> str:
    """
    生成指定长度的字母和数字的随机字符串

    Args:
        length: 随机字符串长度

    Returns:
        str: 随机字符串
    """
    str_list = [random.choice(string.ascii_letters + string.digits) for i in range(length)]
    return ''.join(str_list)


def numeric_random(length: int) -> str:
    """
    生成指定长度的数字随机字符串

    Args:
        length: 随机字符串长度

    Returns:
        str: 随机数字字符串
    """
    str_list = [random.choice(string.digits) for i in range(length)]
    return ''.join(str_list)


def format_datetime(value: datetime) -> str:
    """
    格式化日期时间为字符串

    Args:
        value: datetime 对象

    Returns:
        str: 格式化后的日期时间字符串
    """
    if not value:
        return None
    return value.strftime('%Y-%m-%d %H:%M:%S')


def is_chinese_cellphone(cellphone: str) -> bool:
    """
    判断号码是否为中国的手机号

    Args:
        cellphone: 手机号字符串

    Returns:
        bool: 是否为中国手机号
    """
    match = re.fullmatch(r'1\d{10}', cellphone)
    return bool(match)
