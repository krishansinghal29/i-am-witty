from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from app.application.clock import local_today
from app.application.exceptions import ConflictError, NotFoundError
from app.application.unit_of_work import UnitOfWork
from app.domain.models.daily_plan import DailyPlan
from app.domain.models.task import Task
from app.ports.repositories.daily_plan_repository import (
    CreateDailyPlanInput,
    DailyPlanRepository,
)
from app.ports.repositories.task_attempt_repository import TaskAttemptRepository
from app.ports.repositories.task_repository import TaskRepository
from app.ports.repositories.user_repository import UserRepository

# Priority-ordered rotation of roleplay exercises, each paired with the audio
# lesson that introduces it. "If by X you mean Y" is intentionally absent: it has
# no roleplay variant yet, so it is dropped from the rotation. If a roleplay
# variant is later authored, add it here and it joins the rotation automatically.
ROTATION: tuple[tuple[str, str], ...] = (
    ("roleplay-misinterpretation", "lesson-misinterpretation"),
    ("roleplay-question-answer-tease", "lesson-questionAnswerTease"),
    ("roleplay-sex-with-me-is-like", "lesson-sexWithMeIsLike"),
    ("roleplay-love-hate", "lesson-loveHate"),
    ("roleplay-sexual-misinterpretation", "lesson-sexualMisinterpretation"),
    ("roleplay-push-pull", "lesson-pushPull"),
    ("roleplay-yes-and", "lesson-yesAnd"),
    ("roleplay-first-unusual-thing", "lesson-firstUnusualThing"),
    ("roleplay-vibing", "lesson-vibing"),
    ("roleplay-shit-test", "lesson-shitTest"),
)

# The "welcome to the program" lesson, prepended to every plan until watched once.
INTRO_LESSON_SLUG = "lesson-intro"

_EPOCH = datetime.min.replace(tzinfo=timezone.utc)


class DailyPlanService:
    def __init__(
        self,
        users: UserRepository,
        plans: DailyPlanRepository,
        tasks: TaskRepository,
        attempts: TaskAttemptRepository,
        uow: UnitOfWork,
    ) -> None:
        self._users = users
        self._plans = plans
        self._tasks = tasks
        self._attempts = attempts
        self._uow = uow

    async def get_or_create_today_plan(
        self, app_user_id: uuid.UUID
    ) -> DailyPlan:
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")
        today = local_today(user.timezone)
        plan = await self._plans.get_plan_with_items(app_user_id, today)
        if plan is not None:
            return plan

        # Work in slug space, then resolve to task ids for plan creation.
        catalog_by_slug = {t.slug: t for t in await self._tasks.list_active_catalog()}
        lessons_by_slug = {t.slug: t for t in await self._tasks.list_active_lessons()}

        # Rotation entries that resolve to an active roleplay task today. The
        # paired lesson is optional — a missing lesson just drops that slot.
        rotation: list[tuple[Task, Task | None]] = [
            (catalog_by_slug[ex_slug], lessons_by_slug.get(lesson_slug))
            for ex_slug, lesson_slug in ROTATION
            if ex_slug in catalog_by_slug
        ]
        if not rotation:
            raise ConflictError("no_tasks_available")

        intro = lessons_by_slug.get(INTRO_LESSON_SLUG)

        # One query covers both the rotation (cooldown ordering + carry-over) and
        # the intro "watched?" check — completions from any source.
        lookup_ids = [ex.id for ex, _ in rotation]
        if intro is not None:
            lookup_ids.append(intro.id)
        last_completed = await self._attempts.last_completed_at_by_task(
            app_user_id, lookup_ids
        )

        exercise = await self._choose_exercise(
            app_user_id, today, user.timezone, rotation, last_completed
        )

        # Assemble ordered items: [intro?] + [exercise's lesson?] + [exercise].
        lesson_for = {ex.id: lesson for ex, lesson in rotation}
        task_ids: list[uuid.UUID] = []
        if intro is not None and intro.id not in last_completed:
            task_ids.append(intro.id)
        exercise_lesson = lesson_for.get(exercise.id)
        if exercise_lesson is not None:
            task_ids.append(exercise_lesson.id)
        task_ids.append(exercise.id)

        async with self._uow.transaction():
            plan = await self._plans.create_plan_with_items(
                CreateDailyPlanInput(
                    app_user_id=app_user_id,
                    plan_date=today,
                    timezone=user.timezone,
                    task_ids=tuple(task_ids),
                )
            )
        return plan

    async def _choose_exercise(
        self,
        app_user_id: uuid.UUID,
        today: date,
        tz: str,
        rotation: list[tuple[Task, Task | None]],
        last_completed: dict[uuid.UUID, datetime],
    ) -> Task:
        rotation_by_id = {ex.id: ex for ex, _ in rotation}

        # 1. Carry-over: if the most recent prior plan's exercise was never
        #    completed (roleplay, any source) since it was assigned, re-serve it.
        prev = await self._plans.get_latest_plan_before(app_user_id, today)
        if prev is not None:
            prev_ex = next(
                (
                    rotation_by_id[item.task_id]
                    for item in prev.items
                    if item.task_id in rotation_by_id
                ),
                None,
            )
            if prev_ex is not None and not self._completed_since(
                last_completed.get(prev_ex.id), prev.plan_date, tz
            ):
                return prev_ex

        # 2. Pure rotation: least-recently-done wins; priority index breaks ties.
        #    Never-done share the oldest key, so the highest-priority never-done
        #    exercise is chosen first, walking the list as each gets completed.
        def sort_key(indexed: tuple[int, tuple[Task, Task | None]]) -> tuple[datetime, int]:
            index, (ex, _lesson) = indexed
            return (last_completed.get(ex.id, _EPOCH), index)

        _, (chosen, _lesson) = min(enumerate(rotation), key=sort_key)
        return chosen

    @staticmethod
    def _completed_since(
        completed_at: datetime | None, assigned_date: date, tz: str
    ) -> bool:
        """Whether the exercise was completed on/after the day it was assigned."""
        if completed_at is None:
            return False
        return local_today(tz, now=completed_at) >= assigned_date
