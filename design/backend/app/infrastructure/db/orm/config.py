from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Text,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.orm.base import Base


class AppConfig(Base):
    __tablename__ = "app_config"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[dict] = mapped_column(postgresql.JSONB, nullable=False)
    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    description: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )


class FeatureGateDefault(Base):
    __tablename__ = "feature_gate_defaults"

    feature_key: Mapped[str] = mapped_column(Text, primary_key=True)
    default_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    requires_entitlement: Mapped[str | None] = mapped_column(Text)
    min_app_version: Mapped[str | None] = mapped_column(Text)
    # "metadata" is reserved on the declarative class (Base.metadata), so map a
    # differently-named attribute to the real "metadata" column.
    gate_metadata: Mapped[dict] = mapped_column(
        "metadata",
        postgresql.JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )


class AppReleaseChannel(Base):
    __tablename__ = "app_release_channels"

    channel_key: Mapped[str] = mapped_column(Text, primary_key=True)
    min_supported_version: Mapped[str | None] = mapped_column(Text)
    latest_version: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    # "metadata" is reserved on the declarative class (Base.metadata), so map a
    # differently-named attribute to the real "metadata" column.
    channel_metadata: Mapped[dict] = mapped_column(
        "metadata",
        postgresql.JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )
