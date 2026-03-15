"""
时区工具类
"""

import os
import time
from zoneinfo import ZoneInfo

# 时区配置
TZ = ZoneInfo("Asia/Shanghai")


def setup_timezone():
    """
    设置应用时区

    注意：在 Windows 上，time.tzset() 不可用，会抛出 AttributeError
    """
    os.environ['TZ'] = 'Asia/Shanghai'
    try:
        time.tzset()
    except AttributeError:
        # Windows 系统不支持 tzset()
        pass


def get_timezone():
    """
    获取时区对象

    Returns:
        ZoneInfo: 时区对象
    """
    return TZ


def now_with_timezone():
    """
    获取带时区的当前时间

    Returns:
        datetime: 带时区的当前时间
    """
    from datetime import datetime
    return datetime.now(TZ)
