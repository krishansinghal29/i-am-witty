"""create app_users

Revision ID: 8f5a8545dc4d
Revises: 
Create Date: 2026-06-05 13:47:00.273408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8f5a8545dc4d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Native Postgres enum for the user lifecycle status. Declared with
# create_type=False so this migration owns the CREATE/DROP TYPE ordering
# explicitly; otherwise op.create_table would auto-emit CREATE TYPE and the
# type would leak (never dropped) on downgrade.
user_status = postgresql.ENUM(
    "guest",
    "active",
    "disabled",
    "deleted",
    name="user_status",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    user_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "app_users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("firebase_uid", sa.Text(), nullable=True),
        sa.Column(
            "status",
            user_status,
            server_default=sa.text("'guest'"),
            nullable=False,
        ),
        sa.Column(
            "timezone",
            sa.Text(),
            server_default=sa.text("'UTC'"),
            nullable=False,
        ),
        sa.Column("locale", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_users")),
        sa.UniqueConstraint("firebase_uid", name=op.f("uq_app_users_firebase_uid")),
    )
    op.create_index(
        "app_users_firebase_uid_idx", "app_users", ["firebase_uid"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("app_users_firebase_uid_idx", table_name="app_users")
    op.drop_table("app_users")
    user_status.drop(op.get_bind(), checkfirst=True)
