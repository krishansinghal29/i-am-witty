from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class RecallCueType(str, Enum):
    reaction = "reaction"
    goal = "goal"


class RecallItemKind(str, Enum):
    line = "line"
    concept = "concept"
    routine = "routine"
    focus = "focus"


class RecallItemStatus(str, Enum):
    active = "active"
    paused = "paused"
    archived = "archived"


@dataclass(frozen=True)
class RecallCue:
    """A trigger a line answers: something she says, or a goal you start."""

    id: uuid.UUID
    text: str
    type: RecallCueType


@dataclass(frozen=True)
class RecallItem:
    """One practice item. Which fields are used depends on ``kind``:

    - line: ``cue`` + ``hint`` + ``body`` (the line) + ``delivery_note``
    - concept: ``title`` (name) + ``body`` (definition) + ``scenarios``
    - routine: ``title`` + ``steps``
    - focus: ``title`` + ``question`` + ``body`` (why, optional)
    """

    id: uuid.UUID
    kind: RecallItemKind
    status: RecallItemStatus
    cue: RecallCue | None
    hint: str | None
    title: str | None
    body: str | None
    delivery_note: str | None
    question: str | None
    steps: list[str] | None
    scenarios: list[str] | None
    source: str | None
    created_at: datetime
    updated_at: datetime

    @property
    def cue_id(self) -> uuid.UUID | None:
        return self.cue.id if self.cue is not None else None


@dataclass(frozen=True)
class RecallProgress:
    """A learner's spaced-repetition state for one item."""

    learner_key: str
    item_id: uuid.UUID
    seen_count: int
    first_seen_on: date | None
    last_seen_on: date | None
    due_on: date | None


@dataclass(frozen=True)
class RecallCheckin:
    """A learner's yes/no answer to a focus item on one local date."""

    learner_key: str
    item_id: uuid.UUID
    local_date: date
    done: bool
