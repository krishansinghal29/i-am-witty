from __future__ import annotations

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.orm.base import Base


class TaskAccessTier(str, enum.Enum):
    free = "free"
    premium = "premium"


class TaskStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    future = "future"


class TaskType(Base):
    __tablename__ = "task_types"

    # Text primary key (callers supply ids like 'voice_single_prompt'); no
    # server_default since the application owns id generation.
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    ui_schema_key: Mapped[str] = mapped_column(Text, nullable=False)
    runtime_engine_key: Mapped[str | None] = mapped_column(Text)
    default_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    # "metadata" is reserved on the declarative class (Base.metadata), so map a
    # differently-named attribute to the real "metadata" column.
    type_metadata: Mapped[dict] = mapped_column(
        "metadata",
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
        CheckConstraint(
            "default_duration_seconds > 0",
            name="default_duration_seconds_positive",
        ),
        Index("task_types_ui_schema_idx", "ui_schema_key"),
        Index("task_types_runtime_engine_idx", "runtime_engine_key"),
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    task_type_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("task_types.id"),
        nullable=False,
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    thumbnail_key: Mapped[str] = mapped_column(Text, nullable=False)
    image_key: Mapped[str | None] = mapped_column(Text)
    content: Mapped[dict] = mapped_column(
        postgresql.JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    runtime_config: Mapped[dict] = mapped_column(
        postgresql.JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    access_tier: Mapped[TaskAccessTier] = mapped_column(
        sa.Enum(
            TaskAccessTier,
            name="task_access_tier",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'free'"),
    )
    status: Mapped[TaskStatus] = mapped_column(
        sa.Enum(
            TaskStatus,
            name="task_status",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'active'"),
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    # "metadata" is reserved on the declarative class (Base.metadata), so map a
    # differently-named attribute to the real "metadata" column.
    task_metadata: Mapped[dict] = mapped_column(
        "metadata",
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
        CheckConstraint("duration_seconds > 0", name="duration_seconds_positive"),
        Index("tasks_status_sort_idx", "status", "sort_order"),
        Index("tasks_type_idx", "task_type_id"),
    )
