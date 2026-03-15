#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo 测试任务
"""

import datetime
import logging
import asyncio
from app.jobs.base_job import BaseJob, JobConfig
from app.utils.timezone_utils import get_timezone

logger = logging.getLogger(__name__)


class DemoJob(BaseJob):
    """Demo 测试任务"""

    config = JobConfig(
        id='demo_job',
        name='Demo测试任务',
        trigger='interval',
        seconds=30,
        enabled=True  # 可以通过设置为 False 来禁用
    )

    @staticmethod
    async def run():
        """异步版本的 demo job"""
        logger.info('[demo_job] running (async) at ' + datetime.datetime.now(get_timezone()).strftime('%Y-%m-%d %H:%M:%S'))


# 向后兼容：保留函数导出
run = DemoJob.run
