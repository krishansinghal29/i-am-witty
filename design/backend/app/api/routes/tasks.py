from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.deps import ContainerDep, CurrentUser
from app.application.exceptions import ValidationError
from app.domain.models.task import Task
from app.domain.models.task_attempt import TaskAttemptSource
from app.domain.policies.daily_limit_policy import FreeLimitDecision
from app.ports.task_runtime_engine import GeneratedTaskPayload, StageResponse

router = APIRouter(prefix="/v1", tags=["tasks"])


class TaskResponse(BaseModel):
    """Catalog/runtime view of a task."""

    id: UUID
    slug: str
    title: str
    description: str | None
    task_type_id: str
    duration_seconds: int | None
    thumbnail_key: str | None
    image_key: str | None
    access_tier: str
    status: str
    sort_order: int

    @classmethod
    def from_task(cls, task: Task) -> TaskResponse:
        return cls(
            id=task.id,
            slug=task.slug,
            title=task.title,
            description=task.description,
            task_type_id=task.task_type_id,
            duration_seconds=task.duration_seconds,
            thumbnail_key=task.thumbnail_key,
            image_key=task.image_key,
            access_tier=task.access_tier.value,
            status=task.status.value,
            sort_order=task.sort_order,
        )


class FreeLimitResponse(BaseModel):
    """Free daily-task gating state."""

    allowed: bool
    should_paywall: bool
    remaining: int
    reason: str | None

    @classmethod
    def from_decision(cls, decision: FreeLimitDecision) -> FreeLimitResponse:
        return cls(
            allowed=decision.allowed,
            should_paywall=decision.should_paywall,
            remaining=decision.remaining,
            reason=decision.reason,
        )


class TaskTypeResponse(BaseModel):
    """Runtime descriptor of a task's type."""

    id: str
    display_name: str
    ui_schema_key: str
    runtime_engine_key: str


class MessageResponse(BaseModel):
    role: str
    content: str


class PromptResponse(BaseModel):
    messages: list[MessageResponse]
    speech_text: str | None


class TechniqueResponse(BaseModel):
    name: str
    instruction: str
    example: str


class RolePlayOpeningResponse(BaseModel):
    """Opening turn of a multi-turn roleplay attempt.

    `narration` is shown but not spoken; `dialogue` is her first spoken line
    (also carried in `prompt`/`audio_base64`). Progress counts seed the UI.
    """

    brief_heading: str
    narration: str
    dialogue: str
    target_count: int
    landed_count: int
    appearance: str


class GeneratedPayloadResponse(BaseModel):
    """Generated runtime payload for a freshly started attempt."""

    prompt: PromptResponse
    assigned_technique: TechniqueResponse | None
    scaffold_stages: list[dict]
    audio_base64: str | None
    audio_content_type: str | None
    avatar_image_url: str | None
    roleplay: RolePlayOpeningResponse | None = None

    @classmethod
    def from_payload(cls, payload: GeneratedTaskPayload) -> GeneratedPayloadResponse:
        technique = payload.assigned_technique
        roleplay = payload.roleplay
        return cls(
            prompt=PromptResponse(
                messages=[
                    MessageResponse(role=m.role, content=m.content)
                    for m in payload.prompt.messages
                ],
                speech_text=payload.prompt.speech_text,
            ),
            assigned_technique=(
                TechniqueResponse(
                    name=technique.name,
                    instruction=technique.instruction,
                    example=technique.example,
                )
                if technique is not None
                else None
            ),
            scaffold_stages=[dict(stage) for stage in payload.scaffold_stages],
            audio_base64=payload.audio_base64,
            audio_content_type=payload.audio_content_type,
            avatar_image_url=payload.avatar_image_url,
            roleplay=(
                RolePlayOpeningResponse(
                    brief_heading=roleplay.brief_heading,
                    narration=roleplay.narration,
                    dialogue=roleplay.dialogue,
                    target_count=roleplay.target_count,
                    landed_count=roleplay.landed_count,
                    appearance=roleplay.appearance,
                )
                if roleplay is not None
                else None
            ),
        )


class CatalogItemResponse(BaseModel):
    task: TaskResponse
    requires_premium: bool
    is_locked: bool


class FeedbackTabsResponse(BaseModel):
    """Labels for the two feedback tabs shown on the Reflect phase."""

    feedback_label: str
    sample_answer_label: str


class ContentResponse(BaseModel):
    """Client-renderable labels/limits sourced from ``tasks.content``."""

    prompt_label: str
    response_instruction: str
    recording_limit_seconds: int
    feedback_tabs: FeedbackTabsResponse

    @classmethod
    def from_content(
        cls, content: dict, default_recording_seconds: int
    ) -> ContentResponse:
        """Build from the (possibly partial) ``tasks.content`` dict.

        Every field uses a safe default so a missing key never 500s.
        """
        raw_tabs = content.get("feedback_tabs") or {}
        tabs = raw_tabs if isinstance(raw_tabs, dict) else {}
        recording_limit = content.get("recording_limit_seconds")
        return cls(
            prompt_label=content.get("prompt_label") or "",
            response_instruction=content.get("response_instruction") or "",
            recording_limit_seconds=(
                recording_limit
                if isinstance(recording_limit, int)
                else default_recording_seconds
            ),
            feedback_tabs=FeedbackTabsResponse(
                feedback_label=tabs.get("feedback_label") or "Feedback",
                sample_answer_label=tabs.get("sample_answer_label") or "Better Way",
            ),
        )


class TaskRuntimeResponse(BaseModel):
    attempt_id: UUID
    task: TaskResponse
    task_type: TaskTypeResponse
    content: ContentResponse
    payload: GeneratedPayloadResponse


class StartTaskResponse(BaseModel):
    attempt_id: UUID
    task_id: UUID
    status: str
    free_limit: FreeLimitResponse


class EvaluationResponse(BaseModel):
    style_label: str | None
    feedback_html: str
    sample_answer_html: str
    completion_metadata: dict


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_qualified_date: date


class CompleteTaskResponse(BaseModel):
    attempt_id: UUID
    status: str
    result: EvaluationResponse
    free_limit: FreeLimitResponse
    streak: StreakResponse


class TranscriptionTokenResponse(BaseModel):
    token: str
    expires_at: datetime | None
    provider: str
    extra: dict


class RuntimeRequest(BaseModel):
    source: str = "practice_library"
    daily_plan_item_id: UUID | None = None


class StageResponseBody(BaseModel):
    position: int
    transcript: str


class CompleteRequest(BaseModel):
    client_transcript: str | None = None
    stage_responses: list[StageResponseBody] = Field(default_factory=list)


class TurnRequest(BaseModel):
    client_transcript: str | None = None


class RolePlayTurnResponse(BaseModel):
    """One advance of a roleplay conversation."""

    narration: str
    dialogue: str
    landed: bool
    intensity: str
    landed_count: int
    target_count: int
    is_complete: bool
    sample_answer: str
    audio_base64: str | None
    audio_content_type: str | None


class TurnTaskResponse(BaseModel):
    attempt_id: UUID
    status: str
    turn: RolePlayTurnResponse
    free_limit: FreeLimitResponse
    streak: StreakResponse | None


def _parse_source(source: str) -> TaskAttemptSource:
    """Parse a request source string into a `TaskAttemptSource` (422 on bad value)."""
    try:
        return TaskAttemptSource(source)
    except ValueError as exc:
        raise ValidationError("invalid_source") from exc


@router.get("/catalog", response_model=list[CatalogItemResponse])
async def get_catalog(
    container: ContainerDep, user: CurrentUser
) -> list[CatalogItemResponse]:
    """List the practice catalog with per-user access flags."""
    items = await container.task_catalog_service.get_practice_catalog(user.id)
    return [
        CatalogItemResponse(
            task=TaskResponse.from_task(item.task),
            requires_premium=item.requires_premium,
            is_locked=item.is_locked,
        )
        for item in items
    ]


@router.post("/tasks/{task_id}/runtime", response_model=TaskRuntimeResponse)
async def get_task_runtime(
    task_id: UUID,
    body: RuntimeRequest,
    container: ContainerDep,
    user: CurrentUser,
) -> TaskRuntimeResponse:
    """Start an attempt and return its generated runtime payload."""
    view = await container.task_runtime_service.get_task_runtime(
        user.id, task_id, _parse_source(body.source), body.daily_plan_item_id
    )
    return TaskRuntimeResponse(
        attempt_id=view.attempt.id,
        task=TaskResponse.from_task(view.task),
        task_type=TaskTypeResponse(
            id=view.task_type.id,
            display_name=view.task_type.display_name,
            ui_schema_key=view.task_type.ui_schema_key,
            runtime_engine_key=view.task_type.runtime_engine_key,
        ),
        content=ContentResponse.from_content(
            view.task.content or {},
            view.task.duration_seconds or 30,
        ),
        payload=GeneratedPayloadResponse.from_payload(view.payload),
    )


@router.post("/tasks/{task_id}/start", response_model=StartTaskResponse)
async def start_task(
    task_id: UUID,
    body: RuntimeRequest,
    container: ContainerDep,
    user: CurrentUser,
) -> StartTaskResponse:
    """Start an attempt without generating its runtime payload."""
    result = await container.task_attempt_service.start_task(
        user.id, task_id, _parse_source(body.source), body.daily_plan_item_id
    )
    return StartTaskResponse(
        attempt_id=result.attempt.id,
        task_id=result.task.id,
        status=result.attempt.status.value,
        free_limit=FreeLimitResponse.from_decision(result.free_limit),
    )


@router.post("/attempts/{attempt_id}/complete", response_model=CompleteTaskResponse)
async def complete_task(
    attempt_id: UUID,
    body: CompleteRequest,
    container: ContainerDep,
    user: CurrentUser,
) -> CompleteTaskResponse:
    """Complete an attempt, returning evaluation, gating, and streak state."""
    result = await container.task_attempt_service.complete_task(
        user.id,
        attempt_id,
        client_transcript=body.client_transcript,
        stage_responses=tuple(
            StageResponse(position=s.position, transcript=s.transcript)
            for s in body.stage_responses
        ),
    )
    return CompleteTaskResponse(
        attempt_id=result.attempt.id,
        status=result.attempt.status.value,
        result=EvaluationResponse(
            style_label=result.result.style_label,
            feedback_html=result.result.feedback_html,
            sample_answer_html=result.result.sample_answer_html,
            completion_metadata=result.result.completion_metadata,
        ),
        free_limit=FreeLimitResponse.from_decision(result.free_limit),
        streak=StreakResponse(
            current_streak=result.streak.current_streak,
            longest_streak=result.streak.longest_streak,
            last_qualified_date=result.streak.last_qualified_date,
        ),
    )


@router.post("/attempts/{attempt_id}/turn", response_model=TurnTaskResponse)
async def turn_task(
    attempt_id: UUID,
    body: TurnRequest,
    container: ContainerDep,
    user: CurrentUser,
) -> TurnTaskResponse:
    """Advance a multi-turn (roleplay) attempt by one turn.

    Returns the next AI line + progress; on the goal-reaching turn it also
    finalizes the attempt and returns updated gating + streak state.
    """
    result = await container.task_attempt_service.turn_task(
        user.id,
        attempt_id,
        client_transcript=body.client_transcript,
    )
    turn = result.turn
    return TurnTaskResponse(
        attempt_id=result.attempt.id,
        status=result.attempt.status.value,
        turn=RolePlayTurnResponse(
            narration=turn.narration,
            dialogue=turn.dialogue,
            landed=turn.landed,
            intensity=turn.intensity,
            landed_count=turn.landed_count,
            target_count=turn.target_count,
            is_complete=turn.is_complete,
            sample_answer=turn.sample_answer,
            audio_base64=turn.audio_base64,
            audio_content_type=turn.audio_content_type,
        ),
        free_limit=FreeLimitResponse.from_decision(result.free_limit),
        streak=(
            StreakResponse(
                current_streak=result.streak.current_streak,
                longest_streak=result.streak.longest_streak,
                last_qualified_date=result.streak.last_qualified_date,
            )
            if result.streak is not None
            else None
        ),
    )


@router.post("/transcription-tokens", response_model=TranscriptionTokenResponse)
async def mint_transcription_token(
    container: ContainerDep, user: CurrentUser
) -> TranscriptionTokenResponse:
    """Mint a short-lived client credential for the live-transcript path."""
    cred = await container.transcription_service.mint_ephemeral_credential()
    return TranscriptionTokenResponse(
        token=cred.token,
        expires_at=cred.expires_at,
        provider=cred.provider,
        extra=cred.extra,
    )
