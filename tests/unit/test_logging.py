import json
import logging
from logging.handlers import QueueHandler

import pytest
import structlog

from app.core import logging as core_logging
from app.core.logging import configure_logging


@pytest.fixture(autouse=True)
def _log_env(monkeypatch):
    from config.logging import get_logging_settings

    monkeypatch.setenv("LOG_LEVEL", "INFO")
    get_logging_settings.cache_clear()
    yield
    get_logging_settings.cache_clear()


def _flush_listener():
    # QueueListener.stop() 会先处理完队列再退出，保证日志已写入 stdout
    if core_logging._listener is not None:
        core_logging._listener.stop()
        core_logging._listener = None


def test_json_format_renders_structlog(capfd, monkeypatch):
    monkeypatch.setenv("LOG_FORMAT", "json")
    configure_logging(service="test")
    structlog.get_logger("t").info("hello_event", key="value")
    _flush_listener()
    out = capfd.readouterr().out
    payload = json.loads(out.strip().splitlines()[-1])
    assert payload["event"] == "hello_event"
    assert payload["key"] == "value"
    assert "timestamp" in payload


def test_console_format_writes(capfd, monkeypatch):
    monkeypatch.setenv("LOG_FORMAT", "console")
    configure_logging(service="test")
    structlog.get_logger("t").info("plain_event")
    _flush_listener()
    out = capfd.readouterr().out
    assert "plain_event" in out


def test_queue_handler_installed(monkeypatch):
    monkeypatch.setenv("LOG_FORMAT", "json")
    configure_logging(service="test")
    root = logging.getLogger()
    assert any(isinstance(h, QueueHandler) for h in root.handlers)
    _flush_listener()
