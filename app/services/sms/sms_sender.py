import structlog

logger = structlog.get_logger(__name__)


def send(cellphone, content):
    """发送短信 mock todo"""
    logger.debug("sms_send_mock", cellphone=cellphone)
