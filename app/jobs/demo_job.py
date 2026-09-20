import structlog

from app.jobs.base_job import BaseJob, JobConfig
from app.utils.timezone_utils import now

logger = structlog.get_logger(__name__)


class DemoJob(BaseJob):
    config = JobConfig(
        id="demo_job",
        name="Demo测试任务",
        trigger="interval",
        seconds=30,
        enabled=True,
    )

    @staticmethod
    async def run():
        logger.info("demo_job_running", time=now().isoformat())
