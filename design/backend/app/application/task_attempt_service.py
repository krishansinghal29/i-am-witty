from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.application.clock import local_today, week_start
from app.application.exceptions import (
    AccessDeniedError,
    ConflictError,
    NotFoundError,
    PaywallRequiredError,
    ValidationError,
)
from app.application.runtime_state import rounds_from_state, serialize_runtime_state
from app.application.transcription_service import TranscriptionService
from app.application.unit_of_work import UnitOfWork
from app.infrastructure.runtime.engine_resolver import TaskRuntimeEngineResolver
from app.domain.models.app_user import AppUser
from app.domain.models.entitlement import AccessState
from app.domain.models.task import Task
from app.domain.models.task_attempt import (
    TaskAttempt,
    TaskAttemptSource,
    TaskAttemptStatus,
)
from app.domain.models.task_type import TaskType
from app.domain.policies.daily_limit_policy import (
    FreeLimitDecision,
    FreeLimitState,
    evaluate_free_limit,
)
from app.domain.policies.streak_policy import StreakUpdate, compute_streak_update
from app.domain.policies.task_access_policy import evaluate_task_access
from app.ports.repositories.config_repository import ConfigRepository
from app.ports.repositories.daily_plan_repository import (
    DailyPlanRepository,
    MarkPlanItemCompletedInput,
    MarkPlanItemCurrentInput,
)
from app.ports.repositories.entitlement_repository import EntitlementRepository
from app.ports.repositories.progress_repository import (
    DayActivity,
    ProgressRepository,
    ProgressSummary,
)
from app.ports.repositories.task_attempt_repository import (
    CompleteAttemptInput,
    CreateAttemptInput,
    TaskAttemptRepository,
)
from app.ports.repositories.task_repository import TaskRepository
from app.ports.repositories.usage_repository import UsageRepository
from app.ports.repositories.user_repository import UserRepository
from app.ports.task_runtime_engine import (
    AssignedTechnique,
    CompleteTaskRuntimeInput,
    GeneratedTaskPayload,
    GenerateTaskInput,
    PromptMessage,
    TaskRuntimeResult,
    TurnResult,
    TurnTaskRuntimeInput,
)

def _runtime_context_from_state(
    runtime_state: dict,
    fallback_messages: tuple[PromptMessage, ...],
    fallback_technique: AssignedTechnique | None,
) -> tuple[tuple[PromptMessage, ...], AssignedTechnique | None]:
    """Rebuild the evaluator's prompt context from the attempt's persisted state.

    The generated prompt + assigned technique are stored on the attempt at
    generate time (see ``TaskRuntimeService``). Explicit caller-supplied values
    win when present (used in tests); otherwise we read the persisted state.
    """
    state = runtime_state or {}
    prompt = state.get("prompt") or {}
    raw_messages = prompt.get("messages") or []
    messages = (
        tuple(
            PromptMessage(role=m.get("role", ""), content=m.get("content", ""))
            for m in raw_messages
            if isinstance(m, dict)
        )
        or fallback_messages
    )

    raw_technique = state.get("assigned_technique")
    technique = fallback_technique
    if raw_technique:
        technique = AssignedTechnique(
            name=raw_technique.get("name", ""),
            instruction=raw_technique.get("instruction", ""),
            example=raw_technique.get("example", ""),
        )
    return messages, technique


@dataclass(frozen=True)
class StartTaskResult:
    task: Task
    task_type: TaskType
    attempt: TaskAttempt
    free_limit: FreeLimitDecision


@dataclass(frozen=True)
class RoundProgress:
    """Progress through a multi-rep session (``completed`` of ``total`` reps)."""

    completed: int
    total: int


@dataclass(frozen=True)
class CompleteTaskResult:
    attempt: TaskAttempt
    result: TaskRuntimeResult
    free_limit: FreeLimitDecision
    rounds: RoundProgress
    is_session_complete: bool
    # Populated only on the rep that completes the session (when the shared
    # completion side-effects run); ``None`` for intermediate reps.
    streak: StreakUpdate | None


@dataclass(frozen=True)
class NextRoundResult:
    """A freshly generated scenario for the next rep within the same attempt."""

    attempt: TaskAttempt
    payload: GeneratedTaskPayload
    rounds: RoundProgress
    free_limit: FreeLimitDecision


@dataclass(frozen=True)
class TurnTaskResult:
    """Result of advancing a multi-turn attempt by one turn.

    ``streak`` is populated only on the turn that completes the attempt (when
    the shared completion side-effects run); it is ``None`` for intermediate
    turns.
    """

    attempt: TaskAttempt
    turn: TurnResult
    free_limit: FreeLimitDecision
    streak: StreakUpdate | None


class TaskAttemptService:
    """Owns the start/complete lifecycle of a task attempt.

    Access and free-limit gating run through the pure policies; STT and LLM
    work happens outside any DB transaction so the read transaction is released
    (`rollback`) before external calls and the multi-table write is wrapped in a
    single atomic `transaction`.
    """

    def __init__(
        self,
        users: UserRepository,
        tasks: TaskRepository,
        attempts: TaskAttemptRepository,
        plans: DailyPlanRepository,
        progress: ProgressRepository,
        usage: UsageRepository,
        entitlements: EntitlementRepository,
        config: ConfigRepository,
        transcription: TranscriptionService,
        engines: TaskRuntimeEngineResolver,
        uow: UnitOfWork,
    ) -> None:
        self._users = users
        self._tasks = tasks
        self._attempts = attempts
        self._plans = plans
        self._progress = progress
        self._usage = usage
        self._entitlements = entitlements
        self._config = config
        self._transcription = transcription
        self._engines = engines
        self._uow = uow

    async def _free_limit_for(
        self, user: AppUser, access: AccessState
    ) -> FreeLimitDecision:
        """Compute today's free-task gate from an already-loaded user + access.

        Callers that have just fetched the user and access state pass them in to
        avoid re-querying them (see ``start_task``); ``_free_limit_decision``
        loads them for standalone callers.
        """
        today = local_today(user.timezone)
        du = await self._usage.get_daily_usage(user.id, today)
        limit = await self._config.get_free_task_limit()
        state = FreeLimitState(
            du.free_tasks_completed if du else 0,
            du.free_task_limit if du else limit,
        )
        return evaluate_free_limit(state, access)

    async def _free_limit_decision(self, app_user_id: uuid.UUID) -> FreeLimitDecision:
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")

        access = await self._entitlements.get_access_state(app_user_id)
        return await self._free_limit_for(user, access)

    async def get_free_limit(self, app_user_id: uuid.UUID) -> FreeLimitDecision:
        """Return today's free-task gate without starting an attempt."""
        return await self._free_limit_decision(app_user_id)

    async def start_task(
        self,
        app_user_id: uuid.UUID,
        task_id: uuid.UUID,
        source: TaskAttemptSource,
        daily_plan_item_id: uuid.UUID | None = None,
    ) -> StartTaskResult:
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")

        task = await self._tasks.find_available_by_id(task_id)
        if task is None:
            raise NotFoundError("task_not_found")

        task_type = await self._tasks.get_task_type(task.task_type_id)
        if task_type is None:
            raise NotFoundError("task_type_not_found")

        access = await self._entitlements.get_access_state(app_user_id)

        decision = evaluate_task_access(task, access)
        if not decision.allowed:
            raise AccessDeniedError(decision.reason or "premium_required")

        fl = await self._free_limit_for(user, access)
        # Non-metered task types (lessons) never hit the free-daily-task gate;
        # `fl` is still returned so the client can show the unchanged balance.
        if self._is_metered(task_type) and not fl.allowed:
            raise PaywallRequiredError(fl.reason or "free_limit_reached")

        async with self._uow.transaction():
            attempt = await self._attempts.create_started_attempt(
                CreateAttemptInput(
                    app_user_id=app_user_id,
                    task_id=task_id,
                    source=source,
                    daily_plan_item_id=daily_plan_item_id,
                )
            )
            if daily_plan_item_id is not None:
                await self._plans.mark_item_current(
                    MarkPlanItemCurrentInput(
                        app_user_id=app_user_id,
                        plan_item_id=daily_plan_item_id,
                        current_attempt_id=attempt.id,
                    )
                )

        return StartTaskResult(task, task_type, attempt, fl)

    async def complete_task(
        self,
        app_user_id: uuid.UUID,
        attempt_id: uuid.UUID,
        *,
        client_transcript: str | None = None,
        prompt_messages: tuple[PromptMessage, ...] = (),
        assigned_technique: AssignedTechnique | None = None,
    ) -> CompleteTaskResult:
        # PHASE 1 — reads (inside the request's open read transaction).
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")

        attempt = await self._attempts.find_by_id(attempt_id)
        if attempt is None or attempt.app_user_id != app_user_id:
            raise NotFoundError("attempt_not_found")
        if attempt.status == TaskAttemptStatus.completed:
            raise ConflictError("already_completed")

        task = await self._tasks.find_by_id(attempt.task_id)
        task_type = await self._tasks.get_task_type(task.task_type_id)
        access = await self._entitlements.get_access_state(app_user_id)

        # Release the read transaction before any network call so STT/LLM
        # latency never holds a DB transaction open.
        await self._uow.rollback()

        # Lessons are non-metered consumption: nothing to transcribe or grade,
        # and completion must not touch free-tier usage or the streak. Mark the
        # attempt "listened" via the light path and return.
        if not self._is_metered(task_type):
            return await self._finalize_lesson(user, attempt, access)

        # Rebuild the prompt the user responded to (persisted at generate time)
        # so the evaluator grades against the right scenario/technique.
        eval_messages, eval_technique = _runtime_context_from_state(
            attempt.runtime_state, tuple(prompt_messages), assigned_technique
        )

        # PHASE 2 — external work (no transaction held). The client streamed the
        # transcript directly from the provider; the backend trusts it as-is.
        transcript = self._transcription.resolve_final_transcript(
            client_transcript=client_transcript,
        )
        engine = self._engines.for_task_type(task_type)
        runtime_result = await engine.complete(
            CompleteTaskRuntimeInput(
                task=task,
                task_type=task_type,
                attempt_id=attempt_id,
                prompt_messages=eval_messages,
                transcript=transcript.text,
                assigned_technique=eval_technique,
            )
        )

        # PHASE 3 — advance the rep counter; only the last rep finalizes.
        completed_rounds, total_rounds = rounds_from_state(attempt.runtime_state)
        new_completed = completed_rounds + 1
        is_session_complete = new_completed >= total_rounds
        progress = RoundProgress(completed=new_completed, total=total_rounds)

        if not is_session_complete:
            # Intermediate rep: persist progress, keep the attempt `started`, and
            # skip the shared completion side-effects (streak/usage fire once, on
            # the final rep — mirroring the roleplay turn path).
            new_state = dict(attempt.runtime_state or {})
            new_state["rounds"] = {
                "total": total_rounds,
                "completed": new_completed,
            }
            async with self._uow.transaction():
                await self._attempts.attach_runtime_state(attempt_id, new_state)
            fl = await self._free_limit_for(user, access)
            return CompleteTaskResult(
                attempt, runtime_result, fl, progress, False, None
            )

        # Final rep — atomic multi-table write (shared with the roleplay turn path).
        completion_meta = {
            **runtime_result.completion_metadata,
            "style_label": runtime_result.style_label,
            "feedback_html": runtime_result.feedback_html,
            "sample_answer_html": runtime_result.sample_answer_html,
        }
        completed, fl, streak = await self.finalize_completion(
            user=user,
            attempt=attempt,
            access=access,
            completion_metadata=completion_meta,
        )
        return CompleteTaskResult(
            completed, runtime_result, fl, progress, True, streak
        )

    async def finalize_completion(
        self,
        *,
        user: AppUser,
        attempt: TaskAttempt,
        access: AccessState,
        completion_metadata: dict,
    ) -> tuple[TaskAttempt, FreeLimitDecision, StreakUpdate]:
        """Run the shared completion side-effects for a finished attempt.

        Marks the attempt completed, advances the daily plan item, increments
        free-tier usage (non-plus only), and updates streak + day activity — all
        in one transaction. Shared by single-shot ``complete_task`` and the
        multi-turn ``turn_task`` (when its goal-reaching turn completes).
        """
        today = local_today(user.timezone)
        limit = await self._config.get_free_task_limit()
        du = None
        async with self._uow.transaction():
            completed = await self._attempts.complete_attempt(
                CompleteAttemptInput(
                    attempt_id=attempt.id,
                    completion_metadata=completion_metadata,
                )
            )

            if attempt.daily_plan_item_id is not None:
                await self._plans.mark_item_completed(
                    MarkPlanItemCompletedInput(
                        app_user_id=attempt.app_user_id,
                        plan_item_id=attempt.daily_plan_item_id,
                        attempt_id=attempt.id,
                    )
                )

            if not access.is_riffy_plus:
                du = await self._usage.increment_daily_usage(
                    attempt.app_user_id, today, user.timezone, limit
                )

            summary = await self._progress.get_summary(attempt.app_user_id)
            prev_completed = summary.completed_task_count if summary else 0
            prev_current = summary.current_streak_count if summary else 0
            prev_longest = summary.longest_streak_count if summary else 0
            prev_qualified = summary.last_qualified_streak_date if summary else None
            streak = compute_streak_update(
                prev_current, prev_longest, prev_qualified, today
            )
            await self._progress.update_after_completion(
                attempt.app_user_id,
                ProgressSummary(
                    completed_task_count=prev_completed + 1,
                    current_streak_count=streak.current_streak,
                    longest_streak_count=streak.longest_streak,
                    last_activity_date=today,
                    last_qualified_streak_date=streak.last_qualified_date,
                ),
            )

            ws = week_start(today)
            acts = await self._progress.get_week_activity(attempt.app_user_id, ws)
            existing = next(
                (a for a in acts if a.activity_date == today), None
            )
            day_count = (existing.completed_task_count if existing else 0) + 1
            await self._progress.record_day_activity(
                attempt.app_user_id,
                DayActivity(
                    activity_date=today,
                    timezone=user.timezone,
                    completed_task_count=day_count,
                    had_missed_plan_items=(
                        existing.had_missed_plan_items if existing else False
                    ),
                    streak_qualified=True,
                    streak_protected=(
                        existing.streak_protected if existing else False
                    ),
                ),
            )

        state2 = FreeLimitState(
            du.free_tasks_completed if du else 0,
            du.free_task_limit if du else limit,
        )
        fl = evaluate_free_limit(state2, access)
        return completed, fl, streak

    @staticmethod
    def _is_metered(task_type: TaskType) -> bool:
        """Whether completing this task type counts against the free daily cap.

        Metered is the default; a task type opts out by setting
        ``metered: false`` in its metadata (lessons do). Non-metered types skip
        the free-limit gate on start and the usage/streak side-effects on
        completion.
        """
        return (task_type.metadata or {}).get("metered", True) is not False

    async def _finalize_lesson(
        self,
        user: AppUser,
        attempt: TaskAttempt,
        access: AccessState,
    ) -> CompleteTaskResult:
        """Complete a lesson attempt with no metered side-effects.

        Marks the attempt "listened" (and advances a daily-plan item if one was
        ever linked) but — unlike ``finalize_completion`` — never increments
        free-tier usage, the streak, or day activity. There is nothing to
        evaluate, so the returned result carries empty feedback.
        """
        async with self._uow.transaction():
            completed = await self._attempts.complete_attempt(
                CompleteAttemptInput(
                    attempt_id=attempt.id,
                    completion_metadata={"kind": "lesson"},
                )
            )
            if attempt.daily_plan_item_id is not None:
                await self._plans.mark_item_completed(
                    MarkPlanItemCompletedInput(
                        app_user_id=attempt.app_user_id,
                        plan_item_id=attempt.daily_plan_item_id,
                        attempt_id=attempt.id,
                    )
                )

        fl = await self._free_limit_for(user, access)
        result = TaskRuntimeResult(
            style_label=None,
            feedback_html="",
            sample_answer_html="",
            completion_metadata={"kind": "lesson"},
        )
        return CompleteTaskResult(
            completed,
            result,
            fl,
            RoundProgress(completed=1, total=1),
            is_session_complete=True,
            streak=None,
        )

    async def turn_task(
        self,
        app_user_id: uuid.UUID,
        attempt_id: uuid.UUID,
        *,
        client_transcript: str | None = None,
    ) -> TurnTaskResult:
        """Advance a multi-turn (conversational) attempt by one turn.

        Runs ONE combined LLM call (grade + react + generate next line) against
        the attempt's persisted conversation state, persists the new state, and —
        when the turn completes the goal — runs the shared completion
        side-effects (streak/usage), mirroring ``complete_task``.
        """
        # PHASE 1 — reads (inside the request's open read transaction).
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")

        attempt = await self._attempts.find_by_id(attempt_id)
        if attempt is None or attempt.app_user_id != app_user_id:
            raise NotFoundError("attempt_not_found")
        if attempt.status == TaskAttemptStatus.completed:
            raise ConflictError("already_completed")

        task = await self._tasks.find_by_id(attempt.task_id)
        task_type = await self._tasks.get_task_type(task.task_type_id)
        if not self._engines.supports_turns(task_type):
            raise ValidationError("task_type_not_conversational")
        access = await self._entitlements.get_access_state(app_user_id)

        # Release the read transaction before any network call.
        await self._uow.rollback()

        transcript = self._transcription.resolve_final_transcript(
            client_transcript=client_transcript,
        )
        engine = self._engines.for_task_type(task_type)
        turn = await engine.turn(
            TurnTaskRuntimeInput(
                task=task,
                task_type=task_type,
                attempt_id=attempt_id,
                runtime_state=attempt.runtime_state or {},
                user_transcript=transcript.text,
            )
        )

        # Persist the advanced conversation state.
        async with self._uow.transaction():
            await self._attempts.attach_runtime_state(attempt_id, turn.runtime_state)

        if turn.is_complete:
            completed, fl, streak = await self.finalize_completion(
                user=user,
                attempt=attempt,
                access=access,
                completion_metadata=dict(turn.completion_metadata),
            )
            return TurnTaskResult(completed, turn, fl, streak)

        fl = await self._free_limit_for(user, access)
        return TurnTaskResult(attempt, turn, fl, None)

    async def next_round(
        self,
        app_user_id: uuid.UUID,
        attempt_id: uuid.UUID,
    ) -> NextRoundResult:
        """Generate a fresh scenario for the next rep within the same attempt.

        Called by the "Next" button after an intermediate rep's feedback. Runs a
        new generation (LLM + optional TTS), overwrites the attempt's persisted
        prompt while preserving the rep counter, and returns the new payload so
        the user can record again. Never finalizes — completion happens on the
        final ``complete_task``.
        """
        # PHASE 1 — reads (inside the request's open read transaction).
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")

        attempt = await self._attempts.find_by_id(attempt_id)
        if attempt is None or attempt.app_user_id != app_user_id:
            raise NotFoundError("attempt_not_found")
        if attempt.status == TaskAttemptStatus.completed:
            raise ConflictError("already_completed")

        completed_rounds, total_rounds = rounds_from_state(attempt.runtime_state)
        if completed_rounds >= total_rounds:
            raise ConflictError("session_complete")

        task = await self._tasks.find_by_id(attempt.task_id)
        task_type = await self._tasks.get_task_type(task.task_type_id)
        access = await self._entitlements.get_access_state(app_user_id)

        # Release the read transaction before the generation call.
        await self._uow.rollback()

        engine = self._engines.for_task_type(task_type)
        payload = await engine.generate(
            GenerateTaskInput(
                task=task,
                task_type=task_type,
                attempt_id=attempt_id,
            )
        )

        # Overwrite the prompt for this rep while preserving progress so the next
        # `complete_task` grades the new scenario and advances the same counter.
        new_state = serialize_runtime_state(payload, total_rounds)
        new_state["rounds"]["completed"] = completed_rounds
        async with self._uow.transaction():
            await self._attempts.attach_runtime_state(attempt_id, new_state)

        fl = await self._free_limit_for(user, access)
        return NextRoundResult(
            attempt,
            payload,
            RoundProgress(completed=completed_rounds, total=total_rounds),
            fl,
        )
