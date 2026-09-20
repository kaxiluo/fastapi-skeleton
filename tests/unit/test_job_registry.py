import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.jobs.base_job import BaseJob, JobConfig
from app.jobs.demo_job import DemoJob
from app.jobs.job_registry import JOBS, _resolve_trigger, build_scheduler, register_jobs


class CronJob(BaseJob):
    config = JobConfig(
        id="cron_job",
        name="cron 测试任务",
        trigger="cron",
        cron="*/5 * * * *",
        enabled=True,
    )

    @staticmethod
    async def run():
        pass


class DisabledJob(BaseJob):
    config = JobConfig(
        id="disabled_job", name="禁用", trigger="interval", seconds=60, enabled=False
    )

    @staticmethod
    async def run():
        pass


def test_registry_is_explicit():
    assert [DemoJob] == JOBS


def test_cron_trigger_resolved():
    trigger = _resolve_trigger(CronJob.config)
    assert isinstance(trigger, CronTrigger)


def test_interval_trigger_resolved():
    trigger = _resolve_trigger(JobConfig(id="x", name="x", trigger="interval", seconds=30))
    assert isinstance(trigger, IntervalTrigger)


def test_cron_without_expression_raises():
    with pytest.raises(ValueError, match="cron"):
        _resolve_trigger(JobConfig(id="x", name="x", trigger="cron", cron=None))


def test_register_jobs_registers_enabled_only():
    scheduler = AsyncIOScheduler()
    count = register_jobs(scheduler, jobs=[CronJob, DisabledJob])
    assert count == 1
    assert scheduler.get_job("cron_job") is not None
    assert scheduler.get_job("disabled_job") is None


def test_build_scheduler_has_error_listener():
    scheduler = build_scheduler()
    # APScheduler 无公开 listeners 属性，监听器挂在 _listeners
    assert scheduler._listeners
