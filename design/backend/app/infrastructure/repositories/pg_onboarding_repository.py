from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.onboarding import OnboardingState as OrmOnboardingState
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

    async def create_completed_state(
        self, app_user_id: uuid.UUID, trigger: str
    ) -> OnboardingStateRecord:
        orm = await self._session.get(OrmOnboardingState, app_user_id)
        now = datetime.now(timezone.utc)
        if orm is None:
            orm = OrmOnboardingState(
                app_user_id=app_user_id,
                selected_trigger=OrmOnboardingTrigger(trigger),
                completed_at=now,
            )
            self._session.add(orm)
        else:
            orm.selected_trigger = OrmOnboardingTrigger(trigger)
            orm.completed_at = now
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_record(orm)

    @staticmethod
    def _to_record(orm: OrmOnboardingState) -> OnboardingStateRecord:
        return OnboardingStateRecord(
            app_user_id=orm.app_user_id,
            selected_trigger=(
                orm.selected_trigger.value
                if orm.selected_trigger is not None
                else None
            ),
            completed_at=orm.completed_at,
        )
