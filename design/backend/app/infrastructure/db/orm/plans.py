from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.orm.base import Base


class DailyPlanStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    expired = "expired"


class DailyPlanItemStatus(str, enum.Enum):
    upcoming = "upcoming"
    current = "current"
    completed = "completed"
    missed = "missed"
    skipped = "skipped"


class TaskAttemptSource(str, enum.Enum):
    onboarding = "onboarding"
    daily_plan = "daily_plan"
    practice_library = "practice_library"
    role_play = "role_play"


class TaskAttemptStatus(str, enum.Enum):
    started = "started"
    completed = "completed"
    abandoned = "abandoned"


class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    timezone: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DailyPlanStatus] = mapped_column(
        sa.Enum(
            DailyPlanStatus,
            name="daily_plan_status",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'active'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    __table_args__ = (
        UniqueConstraint("app_user_id", "plan_date"),
        Index(
            "daily_plans_user_date_idx",
            "app_user_id",
            text("plan_date DESC"),
        ),
    )


class DailyPlanItem(Base):
    __tablename__ = "daily_plan_items"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    daily_plan_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("daily_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("tasks.id"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[DailyPlanItemStatus] = mapped_column(
        sa.Enum(
            DailyPlanItemStatus,
            name="daily_plan_item_status",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'upcoming'"),
    )
    # Cyclic FK with task_attempts: daily_plan_items.current_attempt_id ->
    # task_attempts.id and task_attempts.daily_plan_item_id -> daily_plan_items.id.
    # use_alter=True breaks the cycle so this FK is emitted as a separate ALTER
    # after both tables exist (with the doc's explicit constraint name).
    current_attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey(
            "task_attempts.id",
            ondelete="SET NULL",
            use_alter=True,
            name="daily_plan_items_current_attempt_fk",
        ),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    missed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    __table_args__ = (
        UniqueConstraint("daily_plan_id", "position"),
        CheckConstraint("position > 0", name="position_positive"),
        Index(
            "one_current_item_per_plan",
            "daily_plan_id",
            unique=True,
            postgresql_where=text("status = 'current'"),
        ),
        Index(
            "daily_plan_items_plan_status_idx",
            "daily_plan_id",
            "status",
            "position",
        ),
    )


class TaskAttempt(Base):
    __tablename__ = "task_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("tasks.id"),
        nullable=False,
    )
    daily_plan_item_id: Mapped[uuid.UUID | None] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("daily_plan_items.id", ondelete="SET NULL"),
    )
    source: Mapped[TaskAttemptSource] = mapped_column(
        sa.Enum(
            TaskAttemptSource,
            name="task_attempt_source",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    status: Mapped[TaskAttemptStatus] = mapped_column(
        sa.Enum(
            TaskAttemptStatus,
            name="task_attempt_status",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'started'"),
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    abandoned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # "completion_metadata" is NOT reserved (only bare "metadata" is), so it maps
    # directly to its own column.
    completion_metadata: Mapped[dict] = mapped_column(
        postgresql.JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    # Generated runtime context (prompt messages + assigned technique) persisted
    # at generate time so the evaluator can see what the user actually responded
    # to at complete time, without trusting the client to echo it back.
    runtime_state: Mapped[dict] = mapped_column(
        postgresql.JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    __table_args__ = (
        Index(
            "task_attempts_user_started_idx",
            "app_user_id",
            text("started_at DESC"),
        ),
        Index("task_attempts_user_task_idx", "app_user_id", "task_id"),
        Index("task_attempts_plan_item_idx", "daily_plan_item_id"),
    )


class UserDayActivity(Base):
    __tablename__ = "user_day_activity"

    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_date: Mapped[date] = mapped_column(Date, nullable=False)
    timezone: Mapped[str] = mapped_column(Text, nullable=False)
    completed_task_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    had_missed_plan_items: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    streak_qualified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    streak_protected: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    __table_args__ = (
        PrimaryKeyConstraint("app_user_id", "activity_date"),
        CheckConstraint(
            "completed_task_count >= 0", name="completed_task_count_nonneg"
        ),
        Index(
            "user_day_activity_user_date_idx",
            "app_user_id",
            text("activity_date DESC"),
        ),
    )
