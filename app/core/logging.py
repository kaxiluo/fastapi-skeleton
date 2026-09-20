import logging
import logging.handlers
import sys
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from queue import SimpleQueue

import structlog

from config.logging import get_logging_settings

_listener: QueueListener | None = None


class _PassthroughQueueHandler(QueueHandler):
    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        # 默认 prepare 会合并 message 并清空 exc_info/args，
        # 导致 listener 侧 ProcessorFormatter 无法渲染异常栈，因此原样透传
        return record


def configure_logging(service: str = "web") -> None:
    global _listener
    settings = get_logging_settings()

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handlers: list[logging.Handler] = []
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    handlers.append(stream_handler)

    if settings.file_enable:
        log_dir = Path("storage/logs") / service
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_dir / f"{service}.log",
            when="midnight",
            backupCount=settings.retention_days,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(settings.level.upper())

    if _listener is not None:
        _listener.stop()
    queue: SimpleQueue = SimpleQueue()
    root.addHandler(_PassthroughQueueHandler(queue))
    _listener = QueueListener(queue, *handlers)
    _listener.start()

    structlog.configure(
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        cache_logger_on_first_use=True,
    )

    # 访问日志由 RequestContextMiddleware 自写，uvicorn access 日志关闭
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()
    uvicorn_access.propagate = False
