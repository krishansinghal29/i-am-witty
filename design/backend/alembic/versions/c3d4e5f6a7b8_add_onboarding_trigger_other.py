"""add 'other' onboarding trigger value

Revision ID: c3d4e5f6a7b8
Revises: a4b8c9d0e1f2
Create Date: 2026-06-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "a4b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Postgres requires ALTER TYPE ... ADD VALUE to run outside a transaction
    # block, so step out of Alembic's transaction for this statement.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE onboarding_trigger ADD VALUE IF NOT EXISTS 'other'")


def downgrade() -> None:
    # Postgres can't drop an enum value in place, so recreate the type without
    # 'other'. Any rows still set to 'other' are cleared first. The enum is used
    # only by onboarding_states.selected_trigger.
    op.execute(
        "UPDATE onboarding_states SET selected_trigger = NULL "
        "WHERE selected_trigger = 'other'"
    )
    op.execute("ALTER TYPE onboarding_trigger RENAME TO onboarding_trigger_old")
    op.execute(
        "CREATE TYPE onboarding_trigger AS ENUM "
        "('group_chats', 'dates', 'work', 'friends', 'stage', 'teased')"
    )
    op.execute(
        "ALTER TABLE onboarding_states "
        "ALTER COLUMN selected_trigger TYPE onboarding_trigger "
        "USING selected_trigger::text::onboarding_trigger"
    )
    op.execute("DROP TYPE onboarding_trigger_old")
