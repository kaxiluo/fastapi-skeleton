"""create users table

Revision ID: 60c5f6f9c637
Revises:
Create Date: 2026-09-20 21:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "60c5f6f9c637"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("cellphone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column("state", sa.String(length=20), server_default="enabled", nullable=False),
        sa.Column("nickname", sa.String(length=50), nullable=True),
        sa.Column("gender", sa.String(length=20), server_default="unknown", nullable=False),
        sa.Column("avatar", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_cellphone", "users", ["cellphone"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 种子用户仅用于开发/测试引导，生产环境不插入（弱密码后门）
    from config.settings import get_app_settings

    if get_app_settings().is_production:
        return

    users = sa.table(
        "users",
        sa.column("username", sa.String(50)),
        sa.column("password", sa.String(255)),
    )
    op.bulk_insert(
        users,
        [
            {
                "username": "fake_user1",
                "password": "$2b$12$qn3Hjh8zCfYsSnbqHBq63eXjaTwWs4r/SH3yLycDAOTFUi80em6Ju",
            },
            {
                "username": "fake_user2",
                "password": "$2b$12$qn3Hjh8zCfYsSnbqHBq63eXjaTwWs4r/SH3yLycDAOTFUi80em6Ju",
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
