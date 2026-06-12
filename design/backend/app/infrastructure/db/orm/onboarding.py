from __future__ import annotations

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.orm.base import Base


class OnboardingTrigger(str, enum.Enum):
    group_chats = "group_chats"
    dates = "dates"
    work = "work"
    friends = "friends"
    stage = "stage"
    other = "other"
    # Legacy value, no longer offered in onboarding; kept so existing rows and
    # older app builds remain valid.
    teased = "teased"


class OnboardingState(Base):
    """A single row written once, when the user finishes onboarding.

    Onboarding now runs entirely client-side until completion; the only
    persisted facts are the trigger the user picked and the completion time.
    """

    __tablename__ = "onboarding_states"

    app_user_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        primary_key=True,
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
