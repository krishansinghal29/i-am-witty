from __future__ import annotations

import uuid
from dataclasses import dataclass, field
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
class RolePlayOpening:
    """The opening turn of a multi-turn roleplay attempt.

    `narration` is scene/appearance framing shown but never spoken; `dialogue`
    is her first spoken line (TTS'd). `runtime_state` is the full conversational
    state the service persists on the attempt for subsequent `turn` calls.
    """

    brief_heading: str
    narration: str
    dialogue: str
    target_count: int
    landed_count: int
    appearance: str
    runtime_state: dict
    # What the user is expected to do on their first turn for multi-phase
    # roleplays (e.g. "ask" then "tease"). None for single-phase roleplays,
    # where the UI shows no move hint.
    next_user_move: str | None = None


@dataclass(frozen=True)
class CaptionCue:
    """One time-aligned caption fragment for a pre-recorded lesson.

    `start`/`end` are seconds into the audio; `text` is the word (or short
    phrase) spoken during that window. The client highlights the active cue as
    playback advances (the karaoke pattern), so cues are word-level for smooth
    sync. Produced offline by forced alignment, not at request time.
    """

    start: float
    end: float
    text: str


@dataclass(frozen=True)
class GeneratedTaskPayload:
    """Generated runtime payload for a task attempt.

    Optional sections vary by task type: technique tasks populate
    `assigned_technique`, roleplay tasks populate `roleplay`, avatar/audio
    fields are filled only when the provider produces them, and lesson tasks
    populate `audio_url` + `transcript` + `captions` (a pre-recorded audio
    lesson, no generation).
    """

    prompt: GeneratedPrompt
    assigned_technique: AssignedTechnique | None = None
    audio_base64: str | None = None
    audio_content_type: str | None = None
    avatar_image_url: str | None = None
    roleplay: RolePlayOpening | None = None
    # Lesson tasks: a hosted audio file plus its (optionally time-aligned)
    # transcript. `audio_url` streams from the CDN (range requests supported);
    # `captions` is empty until the offline alignment pass produces cues.
    audio_url: str | None = None
    transcript: str | None = None
    captions: tuple[CaptionCue, ...] = ()


@dataclass(frozen=True)
class CompleteTaskRuntimeInput:
    task: Task
    task_type: TaskType
    attempt_id: uuid.UUID
    prompt_messages: tuple[PromptMessage, ...]
    transcript: str
    assigned_technique: AssignedTechnique | None = None


@dataclass(frozen=True)
class TurnTaskRuntimeInput:
    """One advance of a multi-turn (conversational) attempt.

    `runtime_state` is the attempt's persisted conversation/character state from
    the opening (or the previous turn); `user_transcript` is the user's latest
    spoken/typed line.
    """

    task: Task
    task_type: TaskType
    attempt_id: uuid.UUID
    runtime_state: dict
    user_transcript: str


@dataclass(frozen=True)
class TurnResult:
    """Result of advancing a multi-turn attempt.

    `narration` is shown (with a tiny in-world coach note woven in) but not
    spoken; `dialogue` is her next spoken line (TTS'd). `landed`/`intensity`
    drive the progress UI. `is_complete` is true once the goal is reached, at
    which point the service runs the shared completion side-effects.
    `runtime_state` is the new state to persist.

    `is_graded_turn` indicates whether this turn counted as a graded (skill)
    turn. False for setup phases like the "ask" turn of question-answer-tease;
    True for all other turns. The service uses this to gate and increment the
    free-usage counter only for turns that actually practice a skill. Defaults
    to True so engines that don't support multi-phase roleplays are unaffected.
    """

    narration: str
    dialogue: str
    landed: bool
    intensity: str
    landed_count: int
    target_count: int
    is_complete: bool
    runtime_state: dict
    sample_answer: str = ""
    # The phase the user is expected to act in on their NEXT turn for
    # multi-phase roleplays (e.g. "ask"/"tease"). None for single-phase.
    next_user_move: str | None = None
    audio_base64: str | None = None
    audio_content_type: str | None = None
    completion_metadata: dict = field(default_factory=dict)
    is_graded_turn: bool = True


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

    async def turn(self, input: TurnTaskRuntimeInput) -> TurnResult:
        """Advance a multi-turn (conversational) attempt by one turn.

        Only conversational task types support this; single-shot engines may
        raise ``NotImplementedError``. The service gates on the task type's
        ``supports_turns`` metadata before dispatching here.
        """
        ...
