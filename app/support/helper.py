import random
import re
import string
from datetime import datetime


def alphanumeric_random(length: int = 16) -> str:
    """
    生成指定长度的字母和数字的随机字符串
    """
    str_list = [random.choice(string.ascii_letters + string.digits) for i in range(length)]
    return ''.join(str_list)


def numeric_random(length: int) -> str:
    """
    生成指定长度的数字的随机字符串
    """
    str_list = [random.choice(string.digits) for i in range(length)]
    return ''.join(str_list)


def format_datetime(value: datetime):
    if not value:
        return None
    return value.strftime('%Y-%m-%d %H:%M:%S')


def is_chinese_cellphone(cellphone) -> bool:
    """
    判断号码是否为中国的手机号
    """
    match = re.fullmatch(r'1\d{10}', cellphone)
    return bool(match)
