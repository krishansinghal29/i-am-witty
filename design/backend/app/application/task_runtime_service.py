from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.application.runtime_state import serialize_runtime_state
from app.application.task_attempt_service import TaskAttemptService
from app.application.unit_of_work import UnitOfWork
from app.domain.models.task import Task
from app.domain.models.task_attempt import TaskAttempt, TaskAttemptSource
from app.domain.models.task_type import TaskType
from app.infrastructure.runtime.engine_resolver import TaskRuntimeEngineResolver
from app.ports.repositories.task_attempt_repository import TaskAttemptRepository
from app.ports.task_runtime_engine import (
    GeneratedTaskPayload,
    GenerateTaskInput,
)


@dataclass(frozen=True)
class TaskRuntimeView:
    task: Task
    task_type: TaskType
    attempt: TaskAttempt
    payload: GeneratedTaskPayload
    total_rounds: int


def _total_rounds(task: Task) -> int:
    """Reps this task is repeated within one attempt (1 = classic single-shot)."""
    raw = (task.content or {}).get("total_rounds")
    return raw if isinstance(raw, int) and raw > 0 else 1


class TaskRuntimeService:
    """Starts an attempt, generates its runtime payload, and persists its context.

    The attempt is created and committed by ``TaskAttemptService.start_task``
    (which owns its own transaction); payload generation is an external call made
    only after that commit, so a slow generator never holds a lock and the
    started attempt survives even if generation fails. The generated prompt
    context is then written back to the attempt so completion can evaluate
    against it without trusting a client-echoed prompt.
    """

    def __init__(
        self,
        attempt_service: TaskAttemptService,
        engines: TaskRuntimeEngineResolver,
        attempts: TaskAttemptRepository,
        uow: UnitOfWork,
    ) -> None:
        self._attempt_service = attempt_service
        self._engines = engines
        self._attempts = attempts
        self._uow = uow

    async def get_task_runtime(
        self,
        app_user_id: uuid.UUID,
        task_id: uuid.UUID,
        source: TaskAttemptSource,
        daily_plan_item_id: uuid.UUID | None = None,
    ) -> TaskRuntimeView:
        started = await self._attempt_service.start_task(
            app_user_id, task_id, source, daily_plan_item_id
        )
        total_rounds = _total_rounds(started.task)
        engine = self._engines.for_task_type(started.task_type)
        payload = await engine.generate(
            GenerateTaskInput(
                task=started.task,
                task_type=started.task_type,
                attempt_id=started.attempt.id,
            )
        )
        async with self._uow.transaction():
            await self._attempts.attach_runtime_state(
                started.attempt.id,
                serialize_runtime_state(payload, total_rounds),
            )
        return TaskRuntimeView(
            started.task, started.task_type, started.attempt, payload, total_rounds
        )
