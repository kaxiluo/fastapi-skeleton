import os
from pathlib import Path

import pytest


def test_unit_run_not_polluted_by_env_test():
    """守护：make test（-m 'not integration'）时 .env.test 不得注入 unit 进程"""
    if not Path(".env.test").exists():
        pytest.skip(".env.test not present")
    assert os.environ.get("DB_NAME") != "fastapi_test"
    assert os.environ.get("APP_ENV") != "testing"
