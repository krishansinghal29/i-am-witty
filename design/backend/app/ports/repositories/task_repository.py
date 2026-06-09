from __future__ import annotations

import uuid
from typing import Protocol

from app.domain.models.task import Task
from app.domain.models.task_type import TaskType


class TaskRepository(Protocol):
    async def list_active_catalog(self) -> list[Task]: ...

    async def find_by_id(self, task_id: uuid.UUID) -> Task | None: ...

    async def find_by_slug(self, slug: str) -> Task | None: ...

    async def find_available_by_id(self, task_id: uuid.UUID) -> Task | None:
        """Resolve a task only if it is currently active (startable)."""
        ...

    async def get_task_type(self, task_type_id: str) -> TaskType | None: ...
