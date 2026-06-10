"""add manual premium grants

Revision ID: a4b8c9d0e1f2
Revises: b7d4e9f2a1c3
Create Date: 2026-06-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a4b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "b7d4e9f2a1c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "manual_premium_grants",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("app_user_id", sa.UUID(), nullable=False),
        sa.Column(
            "entitlement_key",
            sa.Text(),
            server_default=sa.text("'riffy_plus'"),
            nullable=False,
        ),
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("granted_by", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
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
        sa.CheckConstraint(
            "expires_at > starts_at",
            name=op.f("ck_manual_premium_grants_manual_grant_expiry_after_start"),
        ),
        sa.ForeignKeyConstraint(
            ["app_user_id"],
            ["app_users.id"],
            name=op.f("fk_manual_premium_grants_app_user_id_app_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manual_premium_grants")),
    )
    op.create_index(
        "manual_premium_grants_user_active_idx",
        "manual_premium_grants",
        ["app_user_id", "entitlement_key", "expires_at", "revoked_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "manual_premium_grants_user_active_idx",
        table_name="manual_premium_grants",
    )
    op.drop_table("manual_premium_grants")
