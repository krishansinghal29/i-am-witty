from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from app.domain.models.task_attempt import TaskAttempt, TaskAttemptSource


@dataclass(frozen=True)
class CreateAttemptInput:
    app_user_id: uuid.UUID
    task_id: uuid.UUID
    source: TaskAttemptSource
    daily_plan_item_id: uuid.UUID | None = None


@dataclass(frozen=True)
class CompleteAttemptInput:
    attempt_id: uuid.UUID
    completion_metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class AbandonAttemptInput:
    attempt_id: uuid.UUID
    reason: str | None = None


class TaskAttemptRepository(Protocol):
    async def create_started_attempt(self, input: CreateAttemptInput) -> TaskAttempt: ...

    async def complete_attempt(self, input: CompleteAttemptInput) -> TaskAttempt: ...

    async def abandon_attempt(self, input: AbandonAttemptInput) -> None: ...

    async def find_by_id(self, attempt_id: uuid.UUID) -> TaskAttempt | None: ...

    async def attach_runtime_state(
        self, attempt_id: uuid.UUID, runtime_state: dict
    ) -> None: ...

    async def last_completed_at_by_task(
        self, app_user_id: uuid.UUID, task_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, datetime]:
        """Most recent completion timestamp per task, across attempt sources.

        Returns only tasks the user has actually completed (others are absent
        from the map). Counts completions from any source (daily plan or
        practice library), which drives the daily-plan rotation + carry-over.
        """
        ...
