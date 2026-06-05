from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.task import Task, TaskAccessTier, TaskStatus
from app.domain.models.task_type import TaskType
from app.infrastructure.db.orm.onboarding import (
    OnboardingTrigger as OrmTrigger,
)
from app.infrastructure.db.orm.onboarding import OnboardingTriggerTaskMapping
from app.infrastructure.db.orm.tasks import Task as OrmTask
from app.infrastructure.db.orm.tasks import TaskStatus as OrmTaskStatus
from app.infrastructure.db.orm.tasks import TaskType as OrmTaskType


class PgTaskRepository:
    """Async SQLAlchemy implementation of the task catalog repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active_catalog(self) -> list[Task]:
        stmt = (
            select(OrmTask)
            .where(OrmTask.status == OrmTaskStatus.active)
            .order_by(OrmTask.sort_order)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_domain(row) for row in rows]

    async def find_by_id(self, task_id: uuid.UUID) -> Task | None:
        row = await self._session.get(OrmTask, task_id)
        return self._to_domain(row) if row is not None else None

    async def find_by_slug(self, slug: str) -> Task | None:
        stmt = select(OrmTask).where(OrmTask.slug == slug)
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    async def find_available_by_id(self, task_id: uuid.UUID) -> Task | None:
        stmt = select(OrmTask).where(
            OrmTask.id == task_id,
            OrmTask.status == OrmTaskStatus.active,
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    async def get_task_type(self, task_type_id: str) -> TaskType | None:
        row = await self._session.get(OrmTaskType, task_type_id)
        return self._task_type_to_domain(row) if row is not None else None

    async def list_trigger_task_candidates(self, trigger: str) -> list[Task]:
        stmt = (
            select(OrmTask)
            .join(
                OnboardingTriggerTaskMapping,
                OnboardingTriggerTaskMapping.task_id == OrmTask.id,
            )
            .where(
                OnboardingTriggerTaskMapping.trigger == OrmTrigger(trigger),
                OnboardingTriggerTaskMapping.is_active.is_(True),
            )
            .order_by(OnboardingTriggerTaskMapping.priority.asc())
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_domain(row) for row in rows]

    @staticmethod
    def _to_domain(row: OrmTask) -> Task:
        return Task(
            id=row.id,
            slug=row.slug,
            title=row.title,
            description=row.description,
            task_type_id=row.task_type_id,
            duration_seconds=row.duration_seconds,
            thumbnail_key=row.thumbnail_key,
            image_key=row.image_key,
            content=row.content,
            runtime_config=row.runtime_config,
            access_tier=TaskAccessTier(row.access_tier.value),
            status=TaskStatus(row.status.value),
            sort_order=row.sort_order,
            metadata=row.task_metadata,
        )

    @staticmethod
    def _task_type_to_domain(row: OrmTaskType) -> TaskType:
        return TaskType(
            id=row.id,
            display_name=row.display_name,
            description=row.description,
            ui_schema_key=row.ui_schema_key,
            runtime_engine_key=row.runtime_engine_key,
            default_duration_seconds=row.default_duration_seconds,
            is_active=row.is_active,
            sort_order=row.sort_order,
            metadata=row.type_metadata,
        )
