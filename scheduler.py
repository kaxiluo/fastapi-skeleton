#!/usr/bin/env python3
"""
FastAPI Skeleton 定时任务调度器启动器
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.timezone_utils import setup_timezone
from app.providers.logging_provider import configure_service_logging
from app.providers.database import database_manager
from app.jobs.job_registry import register_jobs


async def register_job(scheduler):
    """
    注册调度任务 - 自动发现并注册所有 Job
    """
    register_jobs(scheduler)


async def main():
    """启动异步定时任务调度器"""
    print("=" * 50)
    print("FastAPI Skeleton Async Task Scheduler Service")
    print("=" * 50)
    print("Starting async task scheduler...")
    print("Press Ctrl+C to stop")
    print()

    # 设置时区
    setup_timezone()

    # 配置调度器服务的日志系统
    configure_service_logging("scheduler")

    logger = logging.getLogger("scheduler")
    logger.info("AsyncIOScheduler initializing")

    # 创建异步调度器
    scheduler = AsyncIOScheduler()

    try:
        # 初始化数据库连接（如果 job 需要的话）
        await database_manager.init_db()
        await database_manager.init_redis()

        # 注册任务
        await register_job(scheduler)

        print("Async scheduler started successfully!")
        print("Registered async tasks will run according to their schedules.")
        print()

        # 启动调度器（会自动保持事件循环运行）
        scheduler.start()

        # 保持调度器运行，直到被中断
        try:
            await asyncio.Future()  # 等待中断信号
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("Received interrupt signal, shutting down...")

    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
    except Exception as e:
        print(f"Scheduler error: {e}")
        logger.error(f"Scheduler error: {e}", exc_info=True)
    finally:
        try:
            if scheduler.running:
                scheduler.shutdown()
            await database_manager.close_db()
            await database_manager.close_redis()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        print("Async scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
