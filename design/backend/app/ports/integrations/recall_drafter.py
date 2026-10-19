from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from app.domain.models.recall import RecallCueType, RecallItemKind


@dataclass(frozen=True)
class CueLineContext:
    """One existing line on a cue, shown to the drafter for context."""

    hint: str | None
    body: str


@dataclass(frozen=True)
class CueContext:
    """An existing cue and its non-archived lines, shown to the drafter."""

    id: uuid.UUID
    text: str
    type: RecallCueType
    lines: list[CueLineContext]


@dataclass(frozen=True)
class DraftedItem:
    """The drafter's raw proposal for one item. Untrusted: the caller validates.

    ``cue_id`` is only ever one of the ids passed in as context (the drafter
    maps its own references back), or ``None`` for a proposed new cue.
    """

    kind: RecallItemKind
    cue_id: uuid.UUID | None
    cue_text: str | None
    cue_type: RecallCueType | None
    hint: str | None
    sibling_hint: str | None
    title: str | None
    body: str | None
    delivery_note: str | None
    question: str | None
    steps: list[str] | None
    scenarios: list[str] | None


class RecallDrafter(Protocol):
    """Swappable AI drafting for the recall admin (an LLM today).

    Every method raises on any provider failure or unusable output; the caller
    decides how to surface that. Nothing here touches the database.
    """

    async def draft_item(
        self, text: str, cues: Sequence[CueContext]
    ) -> DraftedItem:
        """Turn a rough note into one item, reusing a cue from ``cues`` if it fits."""
        ...

    async def draft_scenarios(
        self,
        title: str,
        definition: str | None,
        existing: Sequence[str],
        count: int,
    ) -> list[str]:
        """Write ``count`` new practice scenarios for a concept."""
        ...

    async def draft_hint(
        self,
        line: str,
        cue_text: str | None,
        avoid: Sequence[str],
    ) -> str:
        """Label how ``line`` answers its cue, avoiding the hints in ``avoid``."""
        ...
