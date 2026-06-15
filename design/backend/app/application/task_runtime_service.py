from __future__ import annotations

import uuid
from dataclasses import dataclass

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


def serialize_runtime_state(payload: GeneratedTaskPayload) -> dict:
    """Persistable prompt context for evaluation.

    Stores only what the evaluator needs to re-read the prompt later (messages,
    speech text, assigned technique) — never the generated audio, which is large
    and reproducible.
    """
    technique = payload.assigned_technique
    state: dict = {
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
    # Conversational (roleplay) tasks carry the full turn state to persist so the
    # `turn` endpoint can advance the conversation against it.
    if payload.roleplay is not None:
        state.update(payload.roleplay.runtime_state)
    return state


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
                started.attempt.id, serialize_runtime_state(payload)
            )
        return TaskRuntimeView(
            started.task, started.task_type, started.attempt, payload
        )
