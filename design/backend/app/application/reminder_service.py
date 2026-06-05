from __future__ import annotations

import uuid
from datetime import time

from app.application.exceptions import ValidationError
from app.application.unit_of_work import UnitOfWork
from app.ports.repositories.reminder_repository import (
    ReminderPreference,
    ReminderRepository,
)

# Mirrors ReminderStatus.value strings (comms ORM enum); kept inline so the
# application layer stays free of SQLAlchemy/infrastructure imports.
_VALID_STATUSES = frozenset({"enabled", "skipped", "disabled"})


class ReminderService:
    def __init__(self, reminders: ReminderRepository, uow: UnitOfWork) -> None:
        self._reminders = reminders
        self._uow = uow

    async def get_reminder(
        self, app_user_id: uuid.UUID
    ) -> ReminderPreference | None:
        return await self._reminders.get_preference(app_user_id)

    async def save_reminder(
        self,
        app_user_id: uuid.UUID,
        status: str,
        timing_key: str | None,
        local_time: time | None,
        timezone: str,
    ) -> ReminderPreference:
        if status not in _VALID_STATUSES:
            raise ValidationError("invalid_reminder_status")
        async with self._uow.transaction():
            pref = await self._reminders.save_preference(
                app_user_id, status, timing_key, local_time, timezone
            )
        return pref

    async def clear_reminder(self, app_user_id: uuid.UUID) -> None:
        async with self._uow.transaction():
            await self._reminders.clear_preference(app_user_id)
