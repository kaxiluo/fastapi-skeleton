from alembic.config import Config
from alembic.script import ScriptDirectory

from alembic import command


def test_migrations_chain_is_valid():
    cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    assert len(heads) == 1
    assert script.get_current_head() == heads[0]


def test_offline_upgrade_generates_ddl(capsys):
    # offline 模式（sql=True）只生成 DDL 文本，不连库
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head", sql=True)
    out = capsys.readouterr().out
    assert "CREATE TABLE users" in out
    assert "ix_users_username" in out
