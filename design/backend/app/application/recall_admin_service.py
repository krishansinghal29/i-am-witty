from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from app.application.exceptions import ConflictError, NotFoundError, ValidationError
from app.application.unit_of_work import UnitOfWork
from app.domain.models.recall import (
    RecallCue,
    RecallCueType,
    RecallItem,
    RecallItemKind,
    RecallItemStatus,
)
from app.ports.repositories.recall_repository import (
    CreateRecallItemInput,
    RecallCueWithCount,
    RecallRepository,
)

# Request fields each kind uses; anything else sent for that kind is ignored.
_KIND_FIELDS: dict[RecallItemKind, frozenset[str]] = {
    RecallItemKind.line: frozenset(
        {"cue_id", "new_cue", "hint", "body", "delivery_note", "source"}
    ),
    RecallItemKind.concept: frozenset({"title", "body", "scenarios", "source"}),
    RecallItemKind.routine: frozenset({"title", "steps", "source"}),
    RecallItemKind.focus: frozenset({"title", "question", "body", "source"}),
}


def _clean(value: str | None) -> str | None:
    """Trim a string; empty becomes ``None``."""
    if value is None:
        return None
    value = value.strip()
    return value or None


def _clean_list(values: Sequence[str] | None) -> list[str] | None:
    """Trim each entry and drop blanks; an empty result becomes ``None``."""
    if values is None:
        return None
    cleaned = [value.strip() for value in values if value and value.strip()]
    return cleaned or None


def check_line_hints(hint: str | None, others: Sequence[RecallItem]) -> None:
    """Enforce hint rules for a line joining ``others`` on the same cue.

    ``others`` are the cue's other non-archived lines. Once a cue has two or
    more lines, every line needs a hint and no two hints may match (ignoring
    case), so practice can always say which line it wants.
    """
    if not others:
        return
    if hint is None:
        raise ValidationError("hint_required")
    if any(o.hint is not None and o.hint.lower() == hint.lower() for o in others):
        raise ValidationError("hint_duplicate")
    if any(o.hint is None for o in others):
        raise ValidationError("sibling_hint_missing")


def check_cue_hints(lines: Sequence[RecallItem]) -> None:
    """Enforce the hint rules over all of a cue's non-archived ``lines`` at once.

    Used when a merge brings two cues' lines together: with two or more lines,
    every one needs a hint and no two hints may match (ignoring case).
    """
    if len(lines) < 2:
        return
    if any(line.hint is None for line in lines):
        raise ValidationError("sibling_hint_missing")
    hints = [line.hint.lower() for line in lines if line.hint is not None]
    if len(set(hints)) != len(hints):
        raise ValidationError("hint_duplicate")


class RecallAdminService:
    """Owner-only management of recall cues and items."""

    def __init__(self, recall: RecallRepository, uow: UnitOfWork) -> None:
        self._recall = recall
        self._uow = uow

    # --- cues ---

    async def list_cues(self) -> list[RecallCueWithCount]:
        return await self._recall.list_cues()

    async def create_cue(self, text: str, type: RecallCueType) -> RecallCue:
        cleaned = _clean(text)
        if cleaned is None:
            raise ValidationError("text_required")
        async with self._uow.transaction():
            if await self._recall.find_cue_by_text(cleaned) is not None:
                raise ConflictError("cue_exists")
            return await self._recall.create_cue(cleaned, type)

    async def update_cue(
        self, cue_id: uuid.UUID, changes: Mapping[str, Any]
    ) -> RecallCue:
        text: str | None = None
        if "text" in changes:
            text = _clean(changes["text"])
            if text is None:
                raise ValidationError("text_required")
        type = RecallCueType(changes["type"]) if changes.get("type") else None
        async with self._uow.transaction():
            if await self._recall.find_cue(cue_id) is None:
                raise NotFoundError("cue_not_found")
            if text is not None:
                existing = await self._recall.find_cue_by_text(text)
                if existing is not None and existing.id != cue_id:
                    raise ConflictError("cue_exists")
            return await self._recall.update_cue(cue_id, text, type)

    async def merge_cue(
        self, cue_id: uuid.UUID, into_cue_id: uuid.UUID
    ) -> RecallCueWithCount:
        """Move every line from ``cue_id`` onto ``into_cue_id`` and delete the source.

        Nothing changes if the combined lines would break the hint rules.
        """
        if cue_id == into_cue_id:
            raise ValidationError("merge_same_cue")
        async with self._uow.transaction():
            source = await self._recall.find_cue(cue_id)
            target = await self._recall.find_cue(into_cue_id)
            if source is None or target is None:
                raise NotFoundError("cue_not_found")
            combined = [
                *await self._recall.list_cue_lines(into_cue_id),
                *await self._recall.list_cue_lines(cue_id),
            ]
            check_cue_hints(combined)
            await self._recall.move_cue_lines(cue_id, into_cue_id)
            await self._recall.delete_cue(cue_id)
        return RecallCueWithCount(cue=target, line_count=len(combined))

    # --- items ---

    async def list_items(
        self,
        kind: RecallItemKind | None = None,
        status: RecallItemStatus | None = None,
    ) -> list[RecallItem]:
        return await self._recall.list_items(kind=kind, status=status)

    async def get_item(self, item_id: uuid.UUID) -> RecallItem:
        item = await self._recall.find_item(item_id)
        if item is None:
            raise NotFoundError("item_not_found")
        return item

    async def create_item(
        self, kind: RecallItemKind, fields: Mapping[str, Any]
    ) -> RecallItem:
        fields = {k: v for k, v in fields.items() if k in _KIND_FIELDS[kind]}
        source = _clean(fields.get("source"))

        if kind is RecallItemKind.line:
            return await self._create_line(fields, source)

        title = _clean(fields.get("title"))
        body = _clean(fields.get("body"))
        question = _clean(fields.get("question"))
        steps = _clean_list(fields.get("steps"))
        scenarios = _clean_list(fields.get("scenarios"))
        self._check_required(kind, title, body, question, steps, scenarios)
        async with self._uow.transaction():
            return await self._recall.create_item(
                CreateRecallItemInput(
                    kind=kind,
                    title=title,
                    body=body,
                    question=question,
                    steps=steps,
                    scenarios=scenarios,
                    source=source,
                )
            )

    async def update_item(
        self, item_id: uuid.UUID, changes: Mapping[str, Any]
    ) -> RecallItem:
        item = await self.get_item(item_id)
        if "kind" in changes and RecallItemKind(changes["kind"]) is not item.kind:
            raise ValidationError("kind_immutable")

        allowed = _KIND_FIELDS[item.kind] | {"status"}
        changes = {k: v for k, v in changes.items() if k in allowed}

        columns: dict[str, Any] = {}
        for name in ("hint", "title", "body", "delivery_note", "question", "source"):
            if name in changes:
                columns[name] = _clean(changes[name])
        for name in ("steps", "scenarios"):
            if name in changes:
                columns[name] = _clean_list(changes[name])
        if "status" in changes and changes["status"] is not None:
            columns["status"] = RecallItemStatus(changes["status"])

        def merged(name: str) -> Any:
            return columns[name] if name in columns else getattr(item, name)

        if item.kind is not RecallItemKind.line:
            self._check_required(
                item.kind,
                merged("title"),
                merged("body"),
                merged("question"),
                merged("steps"),
                merged("scenarios"),
            )
            async with self._uow.transaction():
                return await self._recall.update_item(item_id, columns)

        if merged("body") is None:
            raise ValidationError("body_required")
        moves_cue = "cue_id" in changes or "new_cue" in changes
        if moves_cue and (
            (changes.get("cue_id") is None) == (_new_cue_text(changes) is None)
        ):
            raise ValidationError("line_requires_one_cue")

        async with self._uow.transaction():
            cue_id = item.cue_id
            if moves_cue:
                cue = await self._resolve_cue(changes)
                cue_id = cue.id
                columns["cue_id"] = cue_id
            if merged("status") is not RecallItemStatus.archived and cue_id is not None:
                others = [
                    line
                    for line in await self._recall.list_cue_lines(cue_id)
                    if line.id != item_id
                ]
                check_line_hints(merged("hint"), others)
            return await self._recall.update_item(item_id, columns)

    async def _create_line(
        self, fields: Mapping[str, Any], source: str | None
    ) -> RecallItem:
        if (fields.get("cue_id") is None) == (_new_cue_text(fields) is None):
            raise ValidationError("line_requires_one_cue")
        body = _clean(fields.get("body"))
        if body is None:
            raise ValidationError("body_required")
        hint = _clean(fields.get("hint"))

        async with self._uow.transaction():
            cue = await self._resolve_cue(fields)
            check_line_hints(hint, await self._recall.list_cue_lines(cue.id))
            return await self._recall.create_item(
                CreateRecallItemInput(
                    kind=RecallItemKind.line,
                    cue_id=cue.id,
                    hint=hint,
                    body=body,
                    delivery_note=_clean(fields.get("delivery_note")),
                    source=source,
                )
            )

    async def _resolve_cue(self, fields: Mapping[str, Any]) -> RecallCue:
        """Find the line's cue by id, or reuse/create one from ``new_cue``."""
        cue_id = fields.get("cue_id")
        if cue_id is not None:
            cue = await self._recall.find_cue(cue_id)
            if cue is None:
                raise NotFoundError("cue_not_found")
            return cue
        text = _new_cue_text(fields)
        assert text is not None  # guarded by the line_requires_one_cue check
        existing = await self._recall.find_cue_by_text(text)
        if existing is not None:
            return existing
        return await self._recall.create_cue(
            text, RecallCueType(fields["new_cue"]["type"])
        )

    @staticmethod
    def _check_required(
        kind: RecallItemKind,
        title: str | None,
        body: str | None,
        question: str | None,
        steps: list[str] | None,
        scenarios: list[str] | None,
    ) -> None:
        if title is None:
            raise ValidationError("title_required")
        if kind is RecallItemKind.concept:
            if body is None:
                raise ValidationError("body_required")
            if scenarios is None:
                raise ValidationError("scenarios_required")
        elif kind is RecallItemKind.routine:
            if steps is None:
                raise ValidationError("steps_required")
        elif kind is RecallItemKind.focus:
            if question is None:
                raise ValidationError("question_required")


def _new_cue_text(fields: Mapping[str, Any]) -> str | None:
    new_cue = fields.get("new_cue")
    if not new_cue:
        return None
    return _clean(new_cue.get("text"))
