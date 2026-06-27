from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.application.exceptions import NotFoundError
from app.domain.models.task import Task
from app.domain.policies.task_access_policy import evaluate_task_access
from app.ports.repositories.entitlement_repository import EntitlementRepository
from app.ports.repositories.task_repository import TaskRepository


@dataclass(frozen=True)
class CatalogItem:
    task: Task
    requires_premium: bool
    is_locked: bool


class TaskCatalogService:
    def __init__(
        self,
        tasks: TaskRepository,
        entitlements: EntitlementRepository,
    ) -> None:
        self._tasks = tasks
        self._entitlements = entitlements

    async def get_practice_catalog(
        self, app_user_id: uuid.UUID
    ) -> list[CatalogItem]:
        access = await self._entitlements.get_access_state(app_user_id)
        tasks = await self._tasks.list_active_catalog()
        items: list[CatalogItem] = []
        for t in tasks:
            d = evaluate_task_access(t, access)
            items.append(
                CatalogItem(
                    task=t,
                    requires_premium=d.requires_premium,
                    is_locked=not d.allowed,
                )
            )
        return items

    async def get_lessons(self, app_user_id: uuid.UUID) -> list[CatalogItem]:
        """List audio lessons for the Lesson tab (intro first, then exercises).

        Lessons live outside the practice catalog; access flags are still
        evaluated so a future premium lesson locks correctly, though lessons are
        free today and never count against the daily limit.
        """
        access = await self._entitlements.get_access_state(app_user_id)
        lessons = await self._tasks.list_active_lessons()
        return [
            CatalogItem(
                task=t,
                requires_premium=(d := evaluate_task_access(t, access)).requires_premium,
                is_locked=not d.allowed,
            )
            for t in lessons
        ]

    async def get_task_detail(
        self, app_user_id: uuid.UUID, task_id: uuid.UUID
    ) -> CatalogItem:
        t = await self._tasks.find_available_by_id(task_id)
        if t is None:
            raise NotFoundError("task_not_found")
        access = await self._entitlements.get_access_state(app_user_id)
        d = evaluate_task_access(t, access)
        return CatalogItem(
            task=t,
            requires_premium=d.requires_premium,
            is_locked=not d.allowed,
        )
