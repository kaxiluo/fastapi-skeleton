import structlog
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.jobs.base_job import BaseJob, JobConfig
from app.jobs.demo_job import DemoJob
from app.utils.timezone_utils import get_timezone

logger = structlog.get_logger(__name__)

JOBS: list[type[BaseJob]] = [
    DemoJob,
]


def _resolve_trigger(config: JobConfig):
    tz = get_timezone()
    if config.trigger == "cron":
        if not config.cron:
            raise ValueError(f"Job {config.id}: trigger='cron' requires a cron expression")
        return CronTrigger.from_crontab(config.cron, timezone=tz)
    if config.trigger == "interval":
        kwargs = {
            key: value
            for key, value in (
                ("seconds", config.seconds),
                ("minutes", config.minutes),
                ("hours", config.hours),
            )
            if value is not None
        }
        if not kwargs:
            raise ValueError(f"Job {config.id}: trigger='interval' requires seconds/minutes/hours")
        return IntervalTrigger(**kwargs, timezone=tz)
    if config.trigger == "date":
        raise ValueError(f"Job {config.id}: trigger='date' is not configured; use cron/interval")
    raise ValueError(f"Job {config.id}: unknown trigger {config.trigger!r}")


def _on_job_error(event) -> None:
    logger.error(
        "job_execution_failed",
        job_id=getattr(event, "job_id", None),
        exception=str(getattr(event, "exception", "")),
        traceback=getattr(event, "traceback", None),
    )


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_listener(_on_job_error, EVENT_JOB_ERROR)
    return scheduler


def register_jobs(scheduler: AsyncIOScheduler, jobs=None) -> int:
    registered = 0
    for job_class in JOBS if jobs is None else jobs:
        config = job_class.config
        if not config.enabled:
            logger.info("job_disabled", job_id=config.id)
            continue
        trigger = _resolve_trigger(config)
        scheduler.add_job(
            job_class.run,
            trigger=trigger,
            id=config.id,
            name=config.name,
            replace_existing=True,
            max_instances=config.max_instances,
            misfire_grace_time=config.misfire_grace_time,
            coalesce=config.coalesce,
        )
        registered += 1
        logger.info("job_registered", job_id=config.id, trigger=config.trigger)
    logger.info("jobs_registered_total", total=registered)
    return registered
