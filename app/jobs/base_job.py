from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class JobConfig:
    id: str
    name: str
    trigger: str = "interval"  # 'interval' | 'cron' | 'date'
    seconds: int | None = None
    minutes: int | None = None
    hours: int | None = None
    cron: str | None = None  # trigger='cron' 时必填，五段 crontab 表达式
    enabled: bool = True
    max_instances: int = 1
    misfire_grace_time: int | None = None
    coalesce: bool = True


class BaseJob(ABC):
    config: JobConfig

    @staticmethod
    @abstractmethod
    async def run():
        raise NotImplementedError("Job must implement run() method")
