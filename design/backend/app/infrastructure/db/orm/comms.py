from __future__ import annotations

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.orm.base import Base


class NotificationPermissionStatus(str, enum.Enum):
    unknown = "unknown"
    granted = "granted"
    denied = "denied"
    provisional = "provisional"


class SupportMessageStatus(str, enum.Enum):
    received = "received"
    delivered = "delivered"
    failed = "failed"
    closed = "closed"


class NotificationDevice(Base):
    __tablename__ = "notification_devices"

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
    device_key: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    push_token: Mapped[str | None] = mapped_column(Text)
    permission_status: Mapped[NotificationPermissionStatus] = mapped_column(
        sa.Enum(
            NotificationPermissionStatus,
            name="notification_permission_status",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'unknown'"),
    )
    app_version: Mapped[str | None] = mapped_column(Text)
    release_channel: Mapped[str | None] = mapped_column(Text)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
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
        UniqueConstraint("app_user_id", "device_key"),
        Index("notification_devices_user_idx", "app_user_id"),
    )


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    app_user_id: Mapped[uuid.UUID | None] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="SET NULL"),
    )
    source_screen: Mapped[str | None] = mapped_column(Text)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SupportMessageStatus] = mapped_column(
        sa.Enum(
            SupportMessageStatus,
            name="support_message_status",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'received'"),
    )
    routed_to: Mapped[str | None] = mapped_column(Text)
    external_ticket_id: Mapped[str | None] = mapped_column(Text)
    delivery_error: Mapped[str | None] = mapped_column(Text)
    # "metadata" is reserved on the declarative class (Base.metadata), so map a
    # differently-named attribute to the real "metadata" column.
    message_metadata: Mapped[dict] = mapped_column(
        "metadata",
        postgresql.JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("support_messages_status_created_idx", "status", "created_at"),
    )
