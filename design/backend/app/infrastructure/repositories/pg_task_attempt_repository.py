from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.task_attempt import (
    TaskAttempt,
    TaskAttemptSource,
    TaskAttemptStatus,
)
from app.infrastructure.db.orm.plans import TaskAttempt as OrmTaskAttempt
from app.infrastructure.db.orm.plans import TaskAttemptSource as OrmSource
from app.infrastructure.db.orm.plans import TaskAttemptStatus as OrmStatus
from app.ports.repositories.task_attempt_repository import (
    AbandonAttemptInput,
    CompleteAttemptInput,
    CreateAttemptInput,
)


class PgTaskAttemptRepository:
    """Async SQLAlchemy implementation of the task attempt repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_started_attempt(self, input: CreateAttemptInput) -> TaskAttempt:
        attempt = OrmTaskAttempt(
            app_user_id=input.app_user_id,
            task_id=input.task_id,
            daily_plan_item_id=input.daily_plan_item_id,
            source=OrmSource(input.source.value),
        )
        self._session.add(attempt)
        await self._session.flush()
        await self._session.refresh(attempt)
        return self._to_domain(attempt)

    async def complete_attempt(self, input: CompleteAttemptInput) -> TaskAttempt:
        attempt = await self._session.get(OrmTaskAttempt, input.attempt_id)
        if attempt is None:
            raise ValueError(f"task attempt {input.attempt_id} not found")
        attempt.status = OrmStatus(TaskAttemptStatus.completed.value)
        attempt.completed_at = datetime.now(timezone.utc)
        attempt.completion_metadata = {
            **attempt.completion_metadata,
            **input.completion_metadata,
        }
        await self._session.flush()
        await self._session.refresh(attempt)
        return self._to_domain(attempt)

    async def abandon_attempt(self, input: AbandonAttemptInput) -> None:
        attempt = await self._session.get(OrmTaskAttempt, input.attempt_id)
        if attempt is None:
            return
        attempt.status = OrmStatus(TaskAttemptStatus.abandoned.value)
        attempt.abandoned_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def find_by_id(self, attempt_id: uuid.UUID) -> TaskAttempt | None:
        attempt = await self._session.get(OrmTaskAttempt, attempt_id)
        return self._to_domain(attempt) if attempt is not None else None

    @staticmethod
    def _to_domain(row: OrmTaskAttempt) -> TaskAttempt:
        return TaskAttempt(
            id=row.id,
            app_user_id=row.app_user_id,
            task_id=row.task_id,
            daily_plan_item_id=row.daily_plan_item_id,
            source=TaskAttemptSource(row.source.value),
            status=TaskAttemptStatus(row.status.value),
            started_at=row.started_at,
            completed_at=row.completed_at,
            abandoned_at=row.abandoned_at,
            completion_metadata=row.completion_metadata,
        )
