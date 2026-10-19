from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Mapping, Sequence
from dataclasses import dataclass
from typing import TypeVar

from app.application.exceptions import (
    NotFoundError,
    UpstreamUnavailableError,
    ValidationError,
)
from app.application.recall_admin_service import _clean, _clean_list
from app.application.unit_of_work import UnitOfWork
from app.domain.models.recall import (
    RecallCue,
    RecallCueType,
    RecallItem,
    RecallItemKind,
)
from app.ports.integrations.recall_drafter import (
    CueContext,
    CueLineContext,
    DraftedItem,
    RecallDrafter,
)
from app.ports.repositories.recall_repository import RecallRepository

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Concept drafts ask for 3 scenarios; anything past this is dropped.
MAX_DRAFT_SCENARIOS = 5
_QUOTES = "\"'“”‘’"


@dataclass(frozen=True)
class DraftCue:
    """The cue a drafted line answers. ``id`` is set only for an existing cue."""

    id: uuid.UUID | None
    text: str
    type: RecallCueType
    line_count: int  # the existing cue's non-archived lines; 0 for a new cue


@dataclass(frozen=True)
class DraftSiblingHint:
    """A suggested hint for the one existing, hintless line on the matched cue."""

    item_id: uuid.UUID
    body: str
    hint: str


@dataclass(frozen=True)
class RecallDraft:
    """An unsaved item proposal for the admin to review; fields follow ``kind``."""

    kind: RecallItemKind
    cue: DraftCue | None
    hint: str | None
    sibling_hint: DraftSiblingHint | None
    title: str | None
    body: str | None
    delivery_note: str | None
    question: str | None
    steps: list[str] | None
    scenarios: list[str] | None


def _cue_key(text: str) -> str:
    """Compare cue texts ignoring case, surrounding quotes and end punctuation."""
    return text.strip().strip(_QUOTES).rstrip(".!?").strip().lower()


def _clean_cue_text(text: str | None) -> str | None:
    cleaned = _clean(text)
    return _clean(cleaned.strip(_QUOTES)) if cleaned is not None else None


def normalize_hint(hint: str | None) -> str | None:
    """House style: trimmed, lowercase, no wrapping quotes or end punctuation."""
    cleaned = _clean(hint)
    if cleaned is None:
        return None
    return _clean(cleaned.strip(_QUOTES).rstrip(".").lower())


def disambiguate_hint(base: str, taken: set[str]) -> str:
    """``base``, or ``base 2``, ``base 3``... whichever is not in ``taken``."""
    if base not in taken:
        return base
    n = 2
    while f"{base} {n}" in taken:
        n += 1
    return f"{base} {n}"


def resolve_draft_cue(
    drafted: DraftedItem,
    cues: Sequence[RecallCue],
    lines_by_cue: Mapping[uuid.UUID, list[RecallItem]],
) -> tuple[DraftCue, list[RecallItem]] | None:
    """Match a drafted line to an existing cue, or describe the new one.

    The drafter's cue id is trusted only if it names a known cue and its text
    agrees with that cue; otherwise the proposed text is matched against every
    cue, and only if nothing matches is it a new cue. Returns the cue plus the
    existing cue's non-archived lines, or ``None`` when no cue can be formed.
    """
    text = _clean_cue_text(drafted.cue_text)
    by_id = {cue.id: cue for cue in cues}
    cue = by_id.get(drafted.cue_id) if drafted.cue_id is not None else None
    if cue is not None and text is not None and _cue_key(text) != _cue_key(cue.text):
        cue = None
    if cue is None and text is not None:
        cue = next((c for c in cues if _cue_key(c.text) == _cue_key(text)), None)
    if cue is not None:
        lines = lines_by_cue.get(cue.id, [])
        return DraftCue(cue.id, cue.text, cue.type, len(lines)), lines
    if text is None:
        return None
    return DraftCue(None, text, drafted.cue_type or RecallCueType.reaction, 0), []


class RecallAssistService:
    """AI drafting for the recall admin: suggest items, scenarios and hints.

    Reads give the drafter context; the read transaction is released before any
    provider call, and nothing is written. Model output is never trusted for
    ids or hint rules: both are re-derived from the database here.
    """

    def __init__(
        self, recall: RecallRepository, drafter: RecallDrafter, uow: UnitOfWork
    ) -> None:
        self._recall = recall
        self._drafter = drafter
        self._uow = uow

    async def suggest(self, text: str) -> RecallDraft:
        note = _clean(text)
        if note is None:
            raise ValidationError("text_required")

        cues = [entry.cue for entry in await self._recall.list_cues()]
        lines_by_cue: dict[uuid.UUID, list[RecallItem]] = {}
        # list_items is newest first; keep each cue's lines oldest first.
        for line in reversed(await self._recall.list_items(kind=RecallItemKind.line)):
            if line.cue_id is not None:
                lines_by_cue.setdefault(line.cue_id, []).append(line)
        await self._uow.rollback()

        drafted = await self._call(
            self._drafter.draft_item(
                note,
                [
                    CueContext(
                        id=cue.id,
                        text=cue.text,
                        type=cue.type,
                        lines=[
                            CueLineContext(hint=line.hint, body=line.body or "")
                            for line in lines_by_cue.get(cue.id, [])
                        ],
                    )
                    for cue in cues
                ],
            )
        )
        if drafted.kind is RecallItemKind.line:
            return await self._shape_line(drafted, cues, lines_by_cue)
        return self._shape_other(drafted)

    async def draft_scenarios(
        self,
        title: str,
        body: str | None,
        existing: Sequence[str],
        count: int,
    ) -> list[str]:
        name = _clean(title)
        if name is None:
            raise ValidationError("title_required")
        current = _clean_list(existing) or []
        drafted = await self._call(
            self._drafter.draft_scenarios(name, _clean(body), current, count)
        )
        seen = {scenario.lower() for scenario in current}
        fresh: list[str] = []
        for scenario in _clean_list(drafted) or []:
            if scenario.lower() not in seen:
                seen.add(scenario.lower())
                fresh.append(scenario)
        if not fresh:
            raise UpstreamUnavailableError("ai_unavailable")
        return fresh[:count]

    async def draft_hint(
        self, cue_id: uuid.UUID | None, cue_text: str | None, body: str
    ) -> str:
        line = _clean(body)
        if line is None:
            raise ValidationError("body_required")
        taken: list[str] = []
        if cue_id is not None:
            cue = await self._recall.find_cue(cue_id)
            if cue is None:
                raise NotFoundError("cue_not_found")
            cue_text = cue.text
            taken = [
                hint
                for hint in (l.hint for l in await self._recall.list_cue_lines(cue_id))
                if hint is not None
            ]
            await self._uow.rollback()
        proposed = await self._call(
            self._drafter.draft_hint(line, _clean(cue_text), taken)
        )
        return await self._unique_hint(proposed, line, _clean(cue_text), taken)

    async def _shape_line(
        self,
        drafted: DraftedItem,
        cues: Sequence[RecallCue],
        lines_by_cue: Mapping[uuid.UUID, list[RecallItem]],
    ) -> RecallDraft:
        resolved = resolve_draft_cue(drafted, cues, lines_by_cue)
        if resolved is None:
            logger.warning("Recall draft: line came back without a cue")
            raise UpstreamUnavailableError("ai_unavailable")
        cue, existing = resolved
        body = _clean(drafted.body)

        # A hint is only needed once the cue has another line; then it must be
        # unique there, and a lone hintless sibling needs one too.
        hint: str | None = None
        sibling: DraftSiblingHint | None = None
        if existing:
            taken = [line.hint for line in existing if line.hint is not None]
            hint = await self._unique_hint(drafted.hint, body, cue.text, taken)
            if len(existing) == 1 and existing[0].hint is None:
                only = existing[0]
                sibling = DraftSiblingHint(
                    item_id=only.id,
                    body=only.body or "",
                    hint=await self._unique_hint(
                        drafted.sibling_hint, only.body, cue.text, [hint]
                    ),
                )
        return RecallDraft(
            kind=RecallItemKind.line,
            cue=cue,
            hint=hint,
            sibling_hint=sibling,
            title=None,
            body=body,
            delivery_note=_clean(drafted.delivery_note),
            question=None,
            steps=None,
            scenarios=None,
        )

    @staticmethod
    def _shape_other(drafted: DraftedItem) -> RecallDraft:
        kind = drafted.kind
        scenarios = _clean_list(drafted.scenarios)
        return RecallDraft(
            kind=kind,
            cue=None,
            hint=None,
            sibling_hint=None,
            title=_clean(drafted.title),
            body=(
                _clean(drafted.body)
                if kind in (RecallItemKind.concept, RecallItemKind.focus)
                else None
            ),
            delivery_note=None,
            question=_clean(drafted.question) if kind is RecallItemKind.focus else None,
            steps=_clean_list(drafted.steps) if kind is RecallItemKind.routine else None,
            scenarios=(
                scenarios[:MAX_DRAFT_SCENARIOS]
                if kind is RecallItemKind.concept and scenarios is not None
                else None
            ),
        )

    async def _unique_hint(
        self,
        proposed: str | None,
        line: str | None,
        cue_text: str | None,
        taken: Sequence[str],
    ) -> str:
        """``proposed`` if it is free; else ask once more; else number it."""
        taken_keys = {hint.lower() for hint in taken}
        candidate = normalize_hint(proposed)
        if candidate is not None and candidate not in taken_keys:
            return candidate
        retry: str | None = None
        if line:
            try:
                retry = normalize_hint(
                    await self._drafter.draft_hint(line, cue_text, list(taken))
                )
            except Exception as exc:  # noqa: BLE001 - fall back to numbering
                logger.warning("Recall hint retry failed: %s", exc)
        if retry is not None and retry not in taken_keys:
            return retry
        return disambiguate_hint(candidate or retry or "new line", taken_keys)

    @staticmethod
    async def _call(call: Awaitable[T]) -> T:
        """Await a drafter call, surfacing any provider failure as 503."""
        try:
            return await call
        except Exception as exc:  # noqa: BLE001 - any provider failure is upstream
            logger.error("Recall drafter call failed: %s", exc)
            raise UpstreamUnavailableError("ai_unavailable") from exc
