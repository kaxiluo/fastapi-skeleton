#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Job 自动发现和注册器
自动扫描 app/jobs/ 目录并注册所有 Job
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.jobs.base_job import BaseJob, JobConfig

logger = logging.getLogger(__name__)


def discover_jobs() -> List[type]:
    """
    自动发现 app/jobs/ 目录下所有 Job 类

    Returns:
        List[type]: Job 类列表
    """
    jobs = []
    jobs_dir = Path(__file__).parent

    for job_file in jobs_dir.glob('*.py'):
        # 跳过私有文件和 __init__
        if job_file.name.startswith('_'):
            continue

        module_name = f"app.jobs.{job_file.stem}"

        try:
            module = importlib.import_module(module_name)

            # 查找所有 BaseJob 子类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, BaseJob) and
                    obj is not BaseJob and
                    obj.__module__ == module_name):
                    jobs.append(obj)
                    logger.debug(f"Discovered job: {name} from {module_name}")

        except Exception as e:
            logger.error(f"Failed to load job module {module_name}: {e}", exc_info=True)

    return jobs


def register_jobs(scheduler: AsyncIOScheduler) -> int:
    """
    注册所有发现的 Job 到调度器

    Args:
        scheduler: APScheduler 调度器实例

    Returns:
        int: 成功注册的 Job 数量
    """
    jobs = discover_jobs()
    registered_count = 0

    for job_class in jobs:
        try:
            job_config: JobConfig = job_class.config

            # 跳过未定义配置或未启用的 Job
            if not job_config:
                logger.warning(f"Job {job_class.__name__} has no config, skipping")
                continue

            if not job_config.enabled:
                logger.info(f"Job {job_config.name} ({job_config.id}) is disabled, skipping")
                continue

            # 构建触发器参数
            trigger_kwargs = {}
            if job_config.seconds:
                trigger_kwargs['seconds'] = job_config.seconds
            if job_config.minutes:
                trigger_kwargs['minutes'] = job_config.minutes
            if job_config.hours:
                trigger_kwargs['hours'] = job_config.hours

            # 添加 Job 到调度器
            scheduler.add_job(
                job_class.run,
                job_config.trigger,
                id=job_config.id,
                name=job_config.name,
                replace_existing=True,
                max_instances=job_config.max_instances,
                misfire_grace_time=job_config.misfire_grace_time,
                **trigger_kwargs
            )

            registered_count += 1
            logger.info(
                f"[OK] Registered job: {job_config.name} ({job_config.id}) - "
                f"trigger: {job_config.trigger}, "
                f"interval: {trigger_kwargs}"
            )

        except Exception as e:
            logger.error(f"Failed to register job {job_class.__name__}: {e}", exc_info=True)

    logger.info(f"Total jobs registered: {registered_count}/{len(jobs)}")
    return registered_count
