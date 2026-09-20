from datetime import datetime
from zoneinfo import ZoneInfo

from config.settings import get_app_settings


def get_timezone() -> ZoneInfo:
    return ZoneInfo(get_app_settings().timezone)


def now() -> datetime:
    return datetime.now(get_timezone())


def format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    tz = get_timezone()
    if value.tzinfo is None:
        value = value.replace(tzinfo=tz)
    return value.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")


def mysql_timezone_offset() -> str:
    offset = now().strftime("%z")  # e.g. "+0800"
    return f"{offset[:3]}:{offset[3:]}"
