from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.onboarding import OnboardingState as OrmOnboardingState
from app.infrastructure.db.orm.onboarding import OnboardingStep as OrmOnboardingStep
from app.infrastructure.db.orm.onboarding import (
    OnboardingTrigger as OrmOnboardingTrigger,
)
from app.ports.repositories.onboarding_repository import OnboardingStateRecord


class PgOnboardingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_state(
        self, app_user_id: uuid.UUID
    ) -> OnboardingStateRecord | None:
        orm = await self._session.get(OrmOnboardingState, app_user_id)
        return self._to_record(orm) if orm is not None else None

    async def create_initial_state(
        self, app_user_id: uuid.UUID
    ) -> OnboardingStateRecord:
        orm = OrmOnboardingState(app_user_id=app_user_id)
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_record(orm)

    async def save_trigger(
        self, app_user_id: uuid.UUID, trigger: str
    ) -> OnboardingStateRecord:
        orm = await self._session.get(OrmOnboardingState, app_user_id)
        if orm is None:
            orm = OrmOnboardingState(
                app_user_id=app_user_id,
                selected_trigger=OrmOnboardingTrigger(trigger),
            )
            self._session.add(orm)
        else:
            orm.selected_trigger = OrmOnboardingTrigger(trigger)
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_record(orm)

    async def set_first_task(
        self,
        app_user_id: uuid.UUID,
        task_id: uuid.UUID,
        attempt_id: uuid.UUID | None = None,
    ) -> None:
        orm = await self._session.get(OrmOnboardingState, app_user_id)
        if orm is not None:
            orm.first_task_id = task_id
            orm.first_task_attempt_id = attempt_id
            await self._session.flush()

    async def advance_step(self, app_user_id: uuid.UUID, step: str) -> None:
        orm = await self._session.get(OrmOnboardingState, app_user_id)
        if orm is not None:
            orm.current_step = OrmOnboardingStep(step)
            await self._session.flush()

    async def mark_completed(self, app_user_id: uuid.UUID) -> None:
        orm = await self._session.get(OrmOnboardingState, app_user_id)
        if orm is not None:
            orm.current_step = OrmOnboardingStep.complete
            orm.completed_at = datetime.now(timezone.utc)
            await self._session.flush()

    @staticmethod
    def _to_record(orm: OrmOnboardingState) -> OnboardingStateRecord:
        return OnboardingStateRecord(
            app_user_id=orm.app_user_id,
            current_step=orm.current_step.value,
            selected_trigger=(
                orm.selected_trigger.value
                if orm.selected_trigger is not None
                else None
            ),
            first_task_id=orm.first_task_id,
            first_task_attempt_id=orm.first_task_attempt_id,
            first_win_at=orm.first_win_at,
            account_prompt_seen_at=orm.account_prompt_seen_at,
            reminder_prompt_seen_at=orm.reminder_prompt_seen_at,
            completed_at=orm.completed_at,
        )
