from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol

from app.domain.models.recall import (
    RecallAudience,
    RecallCheckin,
    RecallCue,
    RecallCueType,
    RecallItem,
    RecallItemKind,
    RecallItemStatus,
    RecallProgress,
)
from app.domain.policies.recall_schedule_policy import RecallSchedule


@dataclass(frozen=True)
class RecallCueWithCount:
    cue: RecallCue
    line_count: int  # non-archived lines on the cue


@dataclass(frozen=True)
class CreateRecallItemInput:
    kind: RecallItemKind
    cue_id: uuid.UUID | None = None
    hint: str | None = None
    title: str | None = None
    body: str | None = None
    delivery_note: str | None = None
    question: str | None = None
    steps: list[str] | None = None
    scenarios: list[str] | None = None
    source: str | None = None
    audience: RecallAudience = RecallAudience.everyone


class RecallRepository(Protocol):
    # --- cues ---
    async def list_cues(self) -> list[RecallCueWithCount]:
        """All cues ordered by text, each with its non-archived line count."""
        ...

    async def find_cue(self, cue_id: uuid.UUID) -> RecallCue | None: ...

    async def find_cue_by_text(self, text: str) -> RecallCue | None:
        """Case-insensitive exact match on the cue text."""
        ...

    async def create_cue(self, text: str, type: RecallCueType) -> RecallCue: ...

    async def update_cue(
        self, cue_id: uuid.UUID, text: str | None, type: RecallCueType | None
    ) -> RecallCue: ...

    async def move_cue_lines(
        self, from_cue_id: uuid.UUID, to_cue_id: uuid.UUID
    ) -> None:
        """Point every item on ``from_cue_id`` (any status) at ``to_cue_id``."""
        ...

    async def delete_cue(self, cue_id: uuid.UUID) -> None:
        """Delete a cue that no item references any more."""
        ...

    # --- items ---
    async def list_items(
        self,
        kind: RecallItemKind | None = None,
        status: RecallItemStatus | None = None,
    ) -> list[RecallItem]:
        """Newest first. With no ``status`` filter, archived items are excluded."""
        ...

    async def list_non_archived_items(self) -> list[RecallItem]:
        """Active and paused items, oldest first (practice + line positions)."""
        ...

    async def list_cue_lines(self, cue_id: uuid.UUID) -> list[RecallItem]:
        """Non-archived lines on a cue, oldest first."""
        ...

    async def find_item(self, item_id: uuid.UUID) -> RecallItem | None: ...

    async def create_item(self, input: CreateRecallItemInput) -> RecallItem: ...

    async def update_item(
        self, item_id: uuid.UUID, changes: dict[str, Any]
    ) -> RecallItem:
        """Apply column changes (keys are column names, e.g. ``cue_id``)."""
        ...

    # --- learner state ---
    async def list_progress(self, learner_key: str) -> list[RecallProgress]: ...

    async def get_progress_for_update(
        self, learner_key: str, item_id: uuid.UUID
    ) -> RecallProgress | None:
        """Read one progress row, locking it for the rest of the transaction."""
        ...

    async def save_progress(
        self, learner_key: str, item_id: uuid.UUID, schedule: RecallSchedule
    ) -> RecallProgress:
        """Upsert the learner's schedule for the item."""
        ...

    async def list_checkins(
        self, learner_key: str, since: date
    ) -> list[RecallCheckin]:
        """The learner's check-ins on or after ``since``."""
        ...

    async def upsert_checkin(
        self, learner_key: str, item_id: uuid.UUID, local_date: date, done: bool
    ) -> RecallCheckin: ...
