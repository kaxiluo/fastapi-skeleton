import random
import string


def alpha_numeric_random(length: int = 16) -> str:
    """
    生成指定长度的字母和数字的随机字符串
    """
    str_list = [random.choice(string.ascii_letters + string.digits) for i in range(length)]
    return ''.join(str_list)
