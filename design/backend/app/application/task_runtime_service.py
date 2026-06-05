from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.application.task_attempt_service import TaskAttemptService
from app.domain.models.task import Task
from app.domain.models.task_attempt import TaskAttempt, TaskAttemptSource
from app.domain.models.task_type import TaskType
from app.ports.task_runtime_engine import (
    GeneratedTaskPayload,
    GenerateTaskInput,
    TaskRuntimeEngine,
)


@dataclass(frozen=True)
class TaskRuntimeView:
    task: Task
    task_type: TaskType
    attempt: TaskAttempt
    payload: GeneratedTaskPayload


class TaskRuntimeService:
    """Starts an attempt and generates its runtime payload.

    The attempt is created and committed by ``TaskAttemptService.start_task``
    (which owns its own transaction); payload generation is an external call
    made only after that commit, so a slow generator never holds a lock and the
    started attempt survives even if generation fails.
    """

    def __init__(
        self,
        attempt_service: TaskAttemptService,
        engine: TaskRuntimeEngine,
    ) -> None:
        self._attempt_service = attempt_service
        self._engine = engine

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
        payload = await self._engine.generate(
            GenerateTaskInput(
                task=started.task,
                task_type=started.task_type,
                attempt_id=started.attempt.id,
            )
        )
        return TaskRuntimeView(
            started.task, started.task_type, started.attempt, payload
        )
