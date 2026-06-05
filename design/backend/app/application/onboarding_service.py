from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.application.exceptions import ConflictError, ValidationError
from app.application.unit_of_work import UnitOfWork
from app.ports.repositories.onboarding_repository import (
    OnboardingRepository,
    OnboardingStateRecord,
)
from app.ports.repositories.task_repository import TaskRepository
from app.ports.repositories.user_repository import UserRepository

# Mirrors OnboardingTrigger.value strings (ORM enum); kept inline so the
# application layer stays free of SQLAlchemy/infrastructure imports.
_ALLOWED_TRIGGERS = frozenset(
    {"group_chats", "dates", "work", "friends", "stage", "teased"}
)

# OnboardingStep.first_task: the step where the user is ready to do their
# first task, reached right after the trigger is answered.
_FIRST_TASK_STEP = "first_task"


@dataclass(frozen=True)
class OnboardingView:
    state: OnboardingStateRecord
    first_task_id: uuid.UUID


class OnboardingService:
    def __init__(
        self,
        users: UserRepository,
        onboarding: OnboardingRepository,
        tasks: TaskRepository,
        uow: UnitOfWork,
    ) -> None:
        self._users = users
        self._onboarding = onboarding
        self._tasks = tasks
        self._uow = uow

    async def get_or_start(
        self, app_user_id: uuid.UUID
    ) -> OnboardingStateRecord:
        state = await self._onboarding.get_state(app_user_id)
        if state is None:
            async with self._uow.transaction():
                state = await self._onboarding.create_initial_state(app_user_id)
        return state

    async def save_trigger_and_assign_first_task(
        self, app_user_id: uuid.UUID, trigger: str
    ) -> OnboardingView:
        if trigger not in _ALLOWED_TRIGGERS:
            raise ValidationError("invalid_trigger")
        async with self._uow.transaction():
            state = await self._onboarding.save_trigger(app_user_id, trigger)
            candidates = await self._tasks.list_trigger_task_candidates(trigger)
            first = candidates[0] if candidates else None
            if first is None:
                catalog = await self._tasks.list_active_catalog()
                first = catalog[0] if catalog else None
            if first is None:
                raise ConflictError("no_tasks_available")
            await self._onboarding.set_first_task(app_user_id, first.id)
            await self._onboarding.advance_step(app_user_id, _FIRST_TASK_STEP)
        return OnboardingView(state=state, first_task_id=first.id)
