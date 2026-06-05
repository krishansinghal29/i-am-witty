from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol

from app.domain.models.task import Task
from app.domain.models.task_type import TaskType


@dataclass(frozen=True)
class PromptMessage:
    role: str
    content: str


@dataclass(frozen=True)
class GeneratedPrompt:
    messages: tuple[PromptMessage, ...]
    speech_text: str | None = None


@dataclass(frozen=True)
class AssignedTechnique:
    name: str
    instruction: str
    example: str


@dataclass(frozen=True)
class GenerateTaskInput:
    task: Task
    task_type: TaskType
    attempt_id: uuid.UUID


@dataclass(frozen=True)
class GeneratedTaskPayload:
    """Generated runtime payload for a task attempt.

    Optional sections vary by task type: scaffolded tasks populate
    `scaffold_stages`, technique tasks populate `assigned_technique`, and
    avatar/audio fields are filled only when the provider produces them.
    """

    prompt: GeneratedPrompt
    assigned_technique: AssignedTechnique | None = None
    scaffold_stages: tuple[dict, ...] = ()
    audio_base64: str | None = None
    audio_content_type: str | None = None
    avatar_image_url: str | None = None


@dataclass(frozen=True)
class StageResponse:
    position: int
    transcript: str


@dataclass(frozen=True)
class CompleteTaskRuntimeInput:
    task: Task
    task_type: TaskType
    attempt_id: uuid.UUID
    prompt_messages: tuple[PromptMessage, ...]
    transcript: str
    assigned_technique: AssignedTechnique | None = None
    stage_responses: tuple[StageResponse, ...] = ()


@dataclass(frozen=True)
class TaskRuntimeResult:
    """Evaluation output for a completed attempt.

    Mirrors the completion response contract: `feedback_html` carries the four
    feedback sections (What Landed, The Trap, Level Up, Mindset Shift),
    `sample_answer_html` carries the alternative responses, and `style_label`
    is an optional playful label (null for task types that do not classify
    style). `completion_metadata` carries non-rendered context such as
    exercise/evaluator keys.
    """

    style_label: str | None
    feedback_html: str
    sample_answer_html: str
    completion_metadata: dict


class TaskRuntimeEngine(Protocol):
    """Generates a task's runtime payload and evaluates its completion.

    The concrete engine is selected from `runtime_config` per task type and
    encapsulates prompt generation and transcript evaluation. STT and LLM
    calls happen outside the database transaction in `complete_task`.
    """

    async def generate(self, input: GenerateTaskInput) -> GeneratedTaskPayload:
        ...

    async def complete(
        self, input: CompleteTaskRuntimeInput
    ) -> TaskRuntimeResult:
        ...
