from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.recall import (
    RecallCheckin,
    RecallCue,
    RecallCueType,
    RecallItem,
    RecallItemKind,
    RecallItemStatus,
    RecallProgress,
)
from app.domain.policies.recall_schedule_policy import RecallSchedule
from app.infrastructure.db.orm.recall import RecallCheckin as OrmRecallCheckin
from app.infrastructure.db.orm.recall import RecallCue as OrmRecallCue
from app.infrastructure.db.orm.recall import RecallCueType as OrmRecallCueType
from app.infrastructure.db.orm.recall import RecallItem as OrmRecallItem
from app.infrastructure.db.orm.recall import RecallItemKind as OrmRecallItemKind
from app.infrastructure.db.orm.recall import RecallItemStatus as OrmRecallItemStatus
from app.infrastructure.db.orm.recall import RecallProgress as OrmRecallProgress
from app.ports.repositories.recall_repository import (
    CreateRecallItemInput,
    RecallCueWithCount,
)

# Item columns ``update_item`` may write; enums are converted to ORM enums.
_UPDATABLE_ITEM_COLUMNS = frozenset(
    {
        "status",
        "cue_id",
        "hint",
        "title",
        "body",
        "delivery_note",
        "question",
        "steps",
        "scenarios",
        "source",
    }
)


class PgRecallRepository:
    """Async SQLAlchemy implementation of the recall repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- cues ---

    async def list_cues(self) -> list[RecallCueWithCount]:
        line_count = func.count(OrmRecallItem.id)
        stmt = (
            select(OrmRecallCue, line_count)
            .outerjoin(
                OrmRecallItem,
                and_(
                    OrmRecallItem.cue_id == OrmRecallCue.id,
                    OrmRecallItem.kind == OrmRecallItemKind.line,
                    OrmRecallItem.status != OrmRecallItemStatus.archived,
                ),
            )
            .group_by(OrmRecallCue.id)
            .order_by(func.lower(OrmRecallCue.text))
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            RecallCueWithCount(cue=self._cue_to_domain(cue), line_count=count)
            for cue, count in rows
        ]

    async def find_cue(self, cue_id: uuid.UUID) -> RecallCue | None:
        row = await self._session.get(OrmRecallCue, cue_id)
        return self._cue_to_domain(row) if row is not None else None

    async def find_cue_by_text(self, text: str) -> RecallCue | None:
        stmt = select(OrmRecallCue).where(
            func.lower(OrmRecallCue.text) == text.lower()
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._cue_to_domain(row) if row is not None else None

    async def create_cue(self, text: str, type: RecallCueType) -> RecallCue:
        row = OrmRecallCue(text=text, type=OrmRecallCueType(type.value))
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return self._cue_to_domain(row)

    async def update_cue(
        self, cue_id: uuid.UUID, text: str | None, type: RecallCueType | None
    ) -> RecallCue:
        row = await self._session.get(OrmRecallCue, cue_id)
        if row is None:
            raise LookupError(f"recall cue {cue_id} not found")
        if text is not None:
            row.text = text
        if type is not None:
            row.type = OrmRecallCueType(type.value)
        await self._session.flush()
        await self._session.refresh(row)
        return self._cue_to_domain(row)

    # --- items ---

    async def list_items(
        self,
        kind: RecallItemKind | None = None,
        status: RecallItemStatus | None = None,
    ) -> list[RecallItem]:
        stmt = self._items_with_cues()
        if kind is not None:
            stmt = stmt.where(OrmRecallItem.kind == OrmRecallItemKind(kind.value))
        if status is not None:
            stmt = stmt.where(
                OrmRecallItem.status == OrmRecallItemStatus(status.value)
            )
        else:
            stmt = stmt.where(OrmRecallItem.status != OrmRecallItemStatus.archived)
        stmt = stmt.order_by(OrmRecallItem.created_at.desc(), OrmRecallItem.id)
        rows = (await self._session.execute(stmt)).all()
        return [self._item_to_domain(item, cue) for item, cue in rows]

    async def list_non_archived_items(self) -> list[RecallItem]:
        stmt = (
            self._items_with_cues()
            .where(OrmRecallItem.status != OrmRecallItemStatus.archived)
            .order_by(OrmRecallItem.created_at, OrmRecallItem.id)
        )
        rows = (await self._session.execute(stmt)).all()
        return [self._item_to_domain(item, cue) for item, cue in rows]

    async def list_cue_lines(self, cue_id: uuid.UUID) -> list[RecallItem]:
        stmt = (
            self._items_with_cues()
            .where(
                OrmRecallItem.cue_id == cue_id,
                OrmRecallItem.kind == OrmRecallItemKind.line,
                OrmRecallItem.status != OrmRecallItemStatus.archived,
            )
            .order_by(OrmRecallItem.created_at, OrmRecallItem.id)
        )
        rows = (await self._session.execute(stmt)).all()
        return [self._item_to_domain(item, cue) for item, cue in rows]

    async def find_item(self, item_id: uuid.UUID) -> RecallItem | None:
        stmt = self._items_with_cues().where(OrmRecallItem.id == item_id)
        row = (await self._session.execute(stmt)).one_or_none()
        if row is None:
            return None
        item, cue = row
        return self._item_to_domain(item, cue)

    async def create_item(self, input: CreateRecallItemInput) -> RecallItem:
        row = OrmRecallItem(
            kind=OrmRecallItemKind(input.kind.value),
            cue_id=input.cue_id,
            hint=input.hint,
            title=input.title,
            body=input.body,
            delivery_note=input.delivery_note,
            question=input.question,
            steps=input.steps,
            scenarios=input.scenarios,
            source=input.source,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return await self._with_cue(row)

    async def update_item(
        self, item_id: uuid.UUID, changes: dict[str, Any]
    ) -> RecallItem:
        row = await self._session.get(OrmRecallItem, item_id)
        if row is None:
            raise LookupError(f"recall item {item_id} not found")
        for column, value in changes.items():
            if column not in _UPDATABLE_ITEM_COLUMNS:
                raise ValueError(f"recall item column {column!r} is not updatable")
            if column == "status":
                value = OrmRecallItemStatus(value.value)
            setattr(row, column, value)
        await self._session.flush()
        # Reload so the server-side `updated_at` is current.
        await self._session.refresh(row)
        return await self._with_cue(row)

    # --- learner state ---

    async def list_progress(self, learner_key: str) -> list[RecallProgress]:
        stmt = select(OrmRecallProgress).where(
            OrmRecallProgress.learner_key == learner_key
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._progress_to_domain(row) for row in rows]

    async def get_progress_for_update(
        self, learner_key: str, item_id: uuid.UUID
    ) -> RecallProgress | None:
        stmt = (
            select(OrmRecallProgress)
            .where(
                OrmRecallProgress.learner_key == learner_key,
                OrmRecallProgress.item_id == item_id,
            )
            .with_for_update()
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._progress_to_domain(row) if row is not None else None

    async def save_progress(
        self, learner_key: str, item_id: uuid.UUID, schedule: RecallSchedule
    ) -> RecallProgress:
        values = {
            "seen_count": schedule.seen_count,
            "first_seen_on": schedule.first_seen_on,
            "last_seen_on": schedule.last_seen_on,
            "due_on": schedule.due_on,
        }
        stmt = (
            pg_insert(OrmRecallProgress)
            .values(learner_key=learner_key, item_id=item_id, **values)
            .on_conflict_do_update(
                index_elements=[
                    OrmRecallProgress.learner_key,
                    OrmRecallProgress.item_id,
                ],
                set_=values,
            )
        )
        await self._session.execute(stmt)
        return RecallProgress(learner_key=learner_key, item_id=item_id, **values)

    async def list_checkins(
        self, learner_key: str, since: date
    ) -> list[RecallCheckin]:
        stmt = select(OrmRecallCheckin).where(
            OrmRecallCheckin.learner_key == learner_key,
            OrmRecallCheckin.local_date >= since,
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [
            RecallCheckin(
                learner_key=row.learner_key,
                item_id=row.item_id,
                local_date=row.local_date,
                done=row.done,
            )
            for row in rows
        ]

    async def upsert_checkin(
        self, learner_key: str, item_id: uuid.UUID, local_date: date, done: bool
    ) -> RecallCheckin:
        stmt = (
            pg_insert(OrmRecallCheckin)
            .values(
                learner_key=learner_key,
                item_id=item_id,
                local_date=local_date,
                done=done,
            )
            .on_conflict_do_update(
                index_elements=[
                    OrmRecallCheckin.learner_key,
                    OrmRecallCheckin.item_id,
                    OrmRecallCheckin.local_date,
                ],
                set_={"done": done, "updated_at": func.now()},
            )
        )
        await self._session.execute(stmt)
        return RecallCheckin(
            learner_key=learner_key, item_id=item_id, local_date=local_date, done=done
        )

    # --- mapping ---

    @staticmethod
    def _items_with_cues():
        return select(OrmRecallItem, OrmRecallCue).outerjoin(
            OrmRecallCue, OrmRecallItem.cue_id == OrmRecallCue.id
        )

    async def _with_cue(self, row: OrmRecallItem) -> RecallItem:
        cue = (
            await self._session.get(OrmRecallCue, row.cue_id)
            if row.cue_id is not None
            else None
        )
        return self._item_to_domain(row, cue)

    @staticmethod
    def _cue_to_domain(row: OrmRecallCue) -> RecallCue:
        return RecallCue(id=row.id, text=row.text, type=RecallCueType(row.type.value))

    @classmethod
    def _item_to_domain(
        cls, row: OrmRecallItem, cue: OrmRecallCue | None
    ) -> RecallItem:
        return RecallItem(
            id=row.id,
            kind=RecallItemKind(row.kind.value),
            status=RecallItemStatus(row.status.value),
            cue=cls._cue_to_domain(cue) if cue is not None else None,
            hint=row.hint,
            title=row.title,
            body=row.body,
            delivery_note=row.delivery_note,
            question=row.question,
            steps=list(row.steps) if row.steps is not None else None,
            scenarios=list(row.scenarios) if row.scenarios is not None else None,
            source=row.source,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _progress_to_domain(row: OrmRecallProgress) -> RecallProgress:
        return RecallProgress(
            learner_key=row.learner_key,
            item_id=row.item_id,
            seen_count=row.seen_count,
            first_seen_on=row.first_seen_on,
            last_seen_on=row.last_seen_on,
            due_on=row.due_on,
        )
