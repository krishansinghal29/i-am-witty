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
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.orm.base import Base


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    trialing = "trialing"
    past_due = "past_due"
    canceled = "canceled"
    expired = "expired"
    unknown = "unknown"


class DailyUsageCounter(Base):
    __tablename__ = "daily_usage_counters"

    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    usage_date: Mapped[date] = mapped_column(Date, nullable=False)
    timezone: Mapped[str] = mapped_column(Text, nullable=False)
    free_tasks_completed: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    free_task_limit: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("3")
    )
    paywall_shown_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    __table_args__ = (
        PrimaryKeyConstraint("app_user_id", "usage_date"),
        CheckConstraint(
            "free_tasks_completed >= 0", name="free_tasks_completed_nonneg"
        ),
        CheckConstraint("free_task_limit >= 0", name="free_task_limit_nonneg"),
    )


class RevenueCatCustomer(Base):
    __tablename__ = "revenuecat_customers"

    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    revenuecat_app_user_id: Mapped[str] = mapped_column(
        Text, nullable=False, unique=True
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


class SubscriptionEntitlement(Base):
    __tablename__ = "subscription_entitlements"

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
    entitlement_key: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        sa.Enum(
            SubscriptionStatus,
            name="subscription_status",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'unknown'"),
    )
    product_id: Mapped[str | None] = mapped_column(Text)
    period_type: Mapped[str | None] = mapped_column(Text)
    current_period_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    current_period_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    raw_snapshot: Mapped[dict] = mapped_column(
        postgresql.JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    __table_args__ = (
        UniqueConstraint("app_user_id", "entitlement_key"),
        Index(
            "subscription_entitlements_user_status_idx",
            "app_user_id",
            "status",
        ),
    )


class RevenueCatEvent(Base):
    __tablename__ = "revenuecat_events"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    revenuecat_event_id: Mapped[str] = mapped_column(
        Text, nullable=False, unique=True
    )
    app_user_id: Mapped[uuid.UUID | None] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="SET NULL"),
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    entitlement_key: Mapped[str | None] = mapped_column(Text)
    product_id: Mapped[str | None] = mapped_column(Text)
    purchased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict] = mapped_column(postgresql.JSONB, nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("revenuecat_events_app_user_idx", "app_user_id"),
    )
