"""revamp onboarding: drop guests, reminders, task-in-onboarding columns

Collapses onboarding to a single row written at completion (selected_trigger +
completed_at) and removes the guest + reminder + trigger->task machinery:
  - drop guest_sessions (+ support_messages.guest_session_id FK column)
  - drop reminder_preferences
  - drop onboarding_trigger_task_mappings
  - drop onboarding_states.{current_step, first_task_id, first_task_attempt_id,
    first_win_at, account_prompt_seen_at, reminder_prompt_seen_at}
  - drop the now-unused onboarding_step + reminder_status enum types

Revision ID: b7d4e9f2a1c3
Revises: f1a2b3c4d5e6
Create Date: 2026-06-09 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7d4e9f2a1c3'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum types this migration owns the DROP/CREATE of (declared create_type=False
# so ordering is explicit and the types never leak on downgrade).
onboarding_step = postgresql.ENUM(
    "trigger_question",
    "first_task",
    "first_win",
    "account_prompt",
    "reminder_prompt",
    "complete",
    name="onboarding_step",
    create_type=False,
)
reminder_status = postgresql.ENUM(
    "enabled",
    "skipped",
    "disabled",
    name="reminder_status",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    # support_messages first: its FK references guest_sessions, which we drop below.
    op.drop_column("support_messages", "guest_session_id")

    # Collapse onboarding_states to selected_trigger + completed_at. Dropping each
    # column also drops any FK that depended on it (first_task_id -> tasks,
    # first_task_attempt_id -> task_attempts).
    op.drop_column("onboarding_states", "reminder_prompt_seen_at")
    op.drop_column("onboarding_states", "account_prompt_seen_at")
    op.drop_column("onboarding_states", "first_win_at")
    op.drop_column("onboarding_states", "first_task_attempt_id")
    op.drop_column("onboarding_states", "first_task_id")
    op.drop_column("onboarding_states", "current_step")

    op.drop_table("onboarding_trigger_task_mappings")
    op.drop_table("reminder_preferences")
    op.drop_table("guest_sessions")

    bind = op.get_bind()
    onboarding_step.drop(bind, checkfirst=True)
    reminder_status.drop(bind, checkfirst=True)


def downgrade() -> None:
    """Downgrade schema (recreates structures, not data)."""
    bind = op.get_bind()
    onboarding_step.create(bind, checkfirst=True)
    reminder_status.create(bind, checkfirst=True)

    op.create_table(
        "guest_sessions",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("app_user_id", sa.UUID(), nullable=False),
        sa.Column("session_token_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.ForeignKeyConstraint(["app_user_id"], ["app_users.id"], name=op.f("fk_guest_sessions_app_user_id_app_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guest_sessions")),
        sa.UniqueConstraint("session_token_hash", name=op.f("uq_guest_sessions_session_token_hash")),
    )
    op.create_index("guest_sessions_app_user_id_idx", "guest_sessions", ["app_user_id"], unique=False)

    op.create_table(
        "reminder_preferences",
        sa.Column("app_user_id", sa.UUID(), nullable=False),
        sa.Column("status", postgresql.ENUM("enabled", "skipped", "disabled", name="reminder_status", create_type=False), server_default=sa.text("'skipped'"), nullable=False),
        sa.Column("timing_key", sa.Text(), nullable=True),
        sa.Column("local_time", sa.Time(), nullable=True),
        sa.Column("timezone", sa.Text(), server_default=sa.text("'UTC'"), nullable=False),
        sa.Column("last_scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["app_user_id"], ["app_users.id"], name=op.f("fk_reminder_preferences_app_user_id_app_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("app_user_id", name=op.f("pk_reminder_preferences")),
    )

    op.create_table(
        "onboarding_trigger_task_mappings",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("trigger", postgresql.ENUM("group_chats", "dates", "work", "friends", "stage", "teased", name="onboarding_trigger", create_type=False), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("priority", sa.Integer(), server_default=sa.text("100"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], name=op.f("fk_onboarding_trigger_task_mappings_task_id_tasks"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_onboarding_trigger_task_mappings")),
        sa.UniqueConstraint("trigger", "task_id", name="uq_onboarding_trigger_task"),
    )

    # Re-add the onboarding_states columns and their FKs.
    op.add_column(
        "onboarding_states",
        sa.Column("current_step", postgresql.ENUM("trigger_question", "first_task", "first_win", "account_prompt", "reminder_prompt", "complete", name="onboarding_step", create_type=False), server_default=sa.text("'trigger_question'"), nullable=False),
    )
    op.add_column("onboarding_states", sa.Column("first_task_id", sa.UUID(), nullable=True))
    op.add_column("onboarding_states", sa.Column("first_task_attempt_id", sa.UUID(), nullable=True))
    op.add_column("onboarding_states", sa.Column("first_win_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("onboarding_states", sa.Column("account_prompt_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("onboarding_states", sa.Column("reminder_prompt_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(op.f("fk_onboarding_states_first_task_id_tasks"), "onboarding_states", "tasks", ["first_task_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("onboarding_states_first_task_attempt_fk", "onboarding_states", "task_attempts", ["first_task_attempt_id"], ["id"], ondelete="SET NULL")

    # Re-add support_messages.guest_session_id + FK.
    op.add_column("support_messages", sa.Column("guest_session_id", sa.UUID(), nullable=True))
    op.create_foreign_key(op.f("fk_support_messages_guest_session_id_guest_sessions"), "support_messages", "guest_sessions", ["guest_session_id"], ["id"], ondelete="SET NULL")
