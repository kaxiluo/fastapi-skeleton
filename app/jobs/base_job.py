#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Job 基类和配置
定义定时任务的基类和配置数据类
"""

from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass
class JobConfig:
    """Job 配置数据类"""

    id: str  # Job 唯一标识
    name: str  # Job 名称
    trigger: str = 'interval'  # 触发器类型: 'interval', 'cron', 'date'
    seconds: Optional[int] = None  # 间隔秒数
    minutes: Optional[int] = None  # 间隔分钟数
    hours: Optional[int] = None  # 间隔小时数
    cron: Optional[str] = None  # cron 表达式（当 trigger='cron' 时使用）
    enabled: bool = True  # 是否启用
    max_instances: int = 1  # 最大并发实例数
    misfire_grace_time: Optional[int] = None  # 错过执行的宽限时间（秒）


class BaseJob(ABC):
    """Job 基类

    所有定时任务都应该继承此类并定义 config 属性
    """

    # 子类必须覆盖此属性
    config: JobConfig = None

    @staticmethod
    async def run():
        """Job 执行逻辑（子类必须实现）"""
        raise NotImplementedError("Job must implement run() method")
