from __future__ import annotations

import uuid
from dataclasses import dataclass, field
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
