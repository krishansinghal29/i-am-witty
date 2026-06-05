from __future__ import annotations

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.orm.base import Base


class OnboardingStep(str, enum.Enum):
    trigger_question = "trigger_question"
    first_task = "first_task"
    first_win = "first_win"
    account_prompt = "account_prompt"
    reminder_prompt = "reminder_prompt"
    complete = "complete"


class OnboardingTrigger(str, enum.Enum):
    group_chats = "group_chats"
    dates = "dates"
    work = "work"
    friends = "friends"
    stage = "stage"
    teased = "teased"


class OnboardingState(Base):
    __tablename__ = "onboarding_states"

    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    current_step: Mapped[OnboardingStep] = mapped_column(
        sa.Enum(
            OnboardingStep,
            name="onboarding_step",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'trigger_question'"),
    )
    selected_trigger: Mapped[OnboardingTrigger | None] = mapped_column(
        sa.Enum(
            OnboardingTrigger,
            name="onboarding_trigger",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    first_task_id: Mapped[uuid.UUID | None] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
    )
    # references task_attempts(id), but that table does not exist until Batch C,
    # so this stays a plain nullable uuid (no FK) for now. Batch C adds the FK.
    first_task_attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        postgresql.UUID(as_uuid=True)
    )
    first_win_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    account_prompt_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    reminder_prompt_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )


class OnboardingTriggerTaskMapping(Base):
    __tablename__ = "onboarding_trigger_task_mappings"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    # Maps to the "trigger" column; SQLAlchemy quotes the reserved word as needed.
    trigger: Mapped[OnboardingTrigger] = mapped_column(
        sa.Enum(
            OnboardingTrigger,
            name="onboarding_trigger",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("100")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        UniqueConstraint("trigger", "task_id", name="uq_onboarding_trigger_task"),
    )
