from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy import (
    CheckConstraint,
    Date,
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


class UserStatus(str, enum.Enum):
    guest = "guest"
    active = "active"
    disabled = "disabled"
    deleted = "deleted"


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    firebase_uid: Mapped[str | None] = mapped_column(Text, unique=True)
    status: Mapped[UserStatus] = mapped_column(
        sa.Enum(
            UserStatus,
            name="user_status",
            native_enum=True,
            create_type=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'guest'"),
    )
    timezone: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'UTC'")
    )
    locale: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (Index("app_users_firebase_uid_idx", "firebase_uid"),)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    display_name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )


class UserProgressSummary(Base):
    __tablename__ = "user_progress_summaries"

    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    completed_task_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    current_streak_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    longest_streak_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    last_activity_date: Mapped[date | None] = mapped_column(Date)
    last_qualified_streak_date: Mapped[date | None] = mapped_column(Date)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    __table_args__ = (
        CheckConstraint(
            "completed_task_count >= 0", name="completed_task_count_nonneg"
        ),
        CheckConstraint(
            "current_streak_count >= 0", name="current_streak_count_nonneg"
        ),
        CheckConstraint(
            "longest_streak_count >= 0", name="longest_streak_count_nonneg"
        ),
    )
