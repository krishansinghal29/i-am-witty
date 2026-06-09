from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.application.task_attempt_service import TaskAttemptService
from app.application.unit_of_work import UnitOfWork
from app.domain.models.task import Task
from app.domain.models.task_attempt import TaskAttempt, TaskAttemptSource
from app.domain.models.task_type import TaskType
from app.ports.repositories.task_attempt_repository import TaskAttemptRepository
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


def serialize_runtime_state(payload: GeneratedTaskPayload) -> dict:
    """Persistable prompt context for evaluation.

    Stores only what the evaluator needs to re-read the prompt later (messages,
    speech text, assigned technique) — never the generated audio, which is large
    and reproducible.
    """
    technique = payload.assigned_technique
    return {
        "prompt": {
            "messages": [
                {"role": m.role, "content": m.content}
                for m in payload.prompt.messages
            ],
            "speech_text": payload.prompt.speech_text,
        },
        "assigned_technique": (
            {
                "name": technique.name,
                "instruction": technique.instruction,
                "example": technique.example,
            }
            if technique is not None
            else None
        ),
    }


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
        engine: TaskRuntimeEngine,
        attempts: TaskAttemptRepository,
        uow: UnitOfWork,
    ) -> None:
        self._attempt_service = attempt_service
        self._engine = engine
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
        payload = await self._engine.generate(
            GenerateTaskInput(
                task=started.task,
                task_type=started.task_type,
                attempt_id=started.attempt.id,
            )
        )
        async with self._uow.transaction():
            await self._attempts.attach_runtime_state(
                started.attempt.id, serialize_runtime_state(payload)
            )
        return TaskRuntimeView(
            started.task, started.task_type, started.attempt, payload
        )
