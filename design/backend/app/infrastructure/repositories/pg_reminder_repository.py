from __future__ import annotations

import uuid
from datetime import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.comms import ReminderPreference as OrmReminderPreference
from app.infrastructure.db.orm.comms import ReminderStatus
from app.ports.repositories.reminder_repository import (
    ReminderPreference,
    ReminderRepository,
)


class PgReminderRepository(ReminderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_preference(
        self, app_user_id: uuid.UUID
    ) -> ReminderPreference | None:
        row = await self._session.get(OrmReminderPreference, app_user_id)
        if row is None:
            return None
        return self._to_dto(row)

    async def save_preference(
        self,
        app_user_id: uuid.UUID,
        status: str,
        timing_key: str | None,
        local_time: time | None,
        timezone: str,
    ) -> ReminderPreference:
        row = await self._session.get(OrmReminderPreference, app_user_id)
        if row is None:
            row = OrmReminderPreference(app_user_id=app_user_id)
            self._session.add(row)
        row.status = ReminderStatus(status)
        row.timing_key = timing_key
        row.local_time = local_time
        row.timezone = timezone
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_dto(row)

    async def clear_preference(self, app_user_id: uuid.UUID) -> None:
        row = await self._session.get(OrmReminderPreference, app_user_id)
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()

    @staticmethod
    def _to_dto(row: OrmReminderPreference) -> ReminderPreference:
        return ReminderPreference(
            app_user_id=row.app_user_id,
            status=row.status.value,
            timing_key=row.timing_key,
            local_time=row.local_time,
            timezone=row.timezone,
            last_scheduled_at=row.last_scheduled_at,
        )
