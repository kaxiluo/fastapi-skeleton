import asyncio
import contextlib

import structlog

from app.core.db import close_db, init_db
from app.core.logging import configure_logging
from app.core.redis import close_redis, init_redis
from app.jobs.job_registry import build_scheduler, register_jobs
from config.settings import validate_runtime_safety

logger = structlog.get_logger("scheduler")


async def main() -> None:
    configure_logging(service="scheduler")
    validate_runtime_safety()
    scheduler = build_scheduler()
    register_jobs(scheduler)
    await init_db()
    await init_redis()
    scheduler.start()
    logger.info("scheduler_started")
    try:
        await asyncio.Future()
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        await close_redis()
        await close_db()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
