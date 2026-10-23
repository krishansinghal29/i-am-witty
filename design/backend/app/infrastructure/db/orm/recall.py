from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Text,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.orm.base import Base


class RecallCueType(str, enum.Enum):
    reaction = "reaction"
    goal = "goal"


class RecallItemKind(str, enum.Enum):
    line = "line"
    concept = "concept"
    routine = "routine"
    focus = "focus"


class RecallItemStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    archived = "archived"


class RecallAudience(str, enum.Enum):
    everyone = "everyone"
    admin = "admin"


class RecallCue(Base):
    __tablename__ = "recall_cues"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[RecallCueType] = mapped_column(
        sa.Enum(
            RecallCueType,
            name="recall_cue_type",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    # `sa.text` below because the `text` column shadows the bare name in here.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
        onupdate=sa.text("now()"),
    )

    # Cue text is unique ignoring case, so "You're such a player" and
    # "you're such a player" can't become two cues.
    __table_args__ = (
        Index("recall_cues_text_lower_key", sa.text("lower(text)"), unique=True),
    )


class RecallItem(Base):
    __tablename__ = "recall_items"

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    kind: Mapped[RecallItemKind] = mapped_column(
        sa.Enum(
            RecallItemKind,
            name="recall_item_kind",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    status: Mapped[RecallItemStatus] = mapped_column(
        sa.Enum(
            RecallItemStatus,
            name="recall_item_status",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'active'"),
    )
    audience: Mapped[RecallAudience] = mapped_column(
        sa.Enum(
            RecallAudience,
            name="recall_audience",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=text("'everyone'"),
    )
    cue_id: Mapped[uuid.UUID | None] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("recall_cues.id", ondelete="RESTRICT"),
    )
    hint: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    delivery_note: Mapped[str | None] = mapped_column(Text)
    question: Mapped[str | None] = mapped_column(Text)
    steps: Mapped[list | None] = mapped_column(postgresql.JSONB)
    scenarios: Mapped[list | None] = mapped_column(postgresql.JSONB)
    source: Mapped[str | None] = mapped_column(Text)
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
        Index("recall_items_cue_idx", "cue_id"),
        Index("recall_items_kind_status_idx", "kind", "status"),
    )


class RecallProgress(Base):
    __tablename__ = "recall_progress"

    # "anon:<uuid>" for anonymous visitors, "uid:<firebase uid>" for the admin.
    learner_key: Mapped[str] = mapped_column(Text, nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("recall_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    seen_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    first_seen_on: Mapped[date | None] = mapped_column(Date)
    last_seen_on: Mapped[date | None] = mapped_column(Date)
    due_on: Mapped[date | None] = mapped_column(Date)

    __table_args__ = (
        PrimaryKeyConstraint("learner_key", "item_id"),
        Index("recall_progress_learner_due_idx", "learner_key", "due_on"),
    )


class RecallCheckin(Base):
    __tablename__ = "recall_checkins"

    learner_key: Mapped[str] = mapped_column(Text, nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("recall_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    local_date: Mapped[date] = mapped_column(Date, nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    __table_args__ = (PrimaryKeyConstraint("learner_key", "item_id", "local_date"),)
