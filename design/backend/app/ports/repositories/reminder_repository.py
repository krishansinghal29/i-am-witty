from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, time
from typing import Protocol


@dataclass(frozen=True)
class ReminderPreference:
    app_user_id: uuid.UUID
    status: str
    timing_key: str | None
    local_time: time | None
    timezone: str
    last_scheduled_at: datetime | None


class ReminderRepository(Protocol):
    async def get_preference(
        self, app_user_id: uuid.UUID
    ) -> ReminderPreference | None: ...

    async def save_preference(
        self,
        app_user_id: uuid.UUID,
        status: str,
        timing_key: str | None,
        local_time: time | None,
        timezone: str,
    ) -> ReminderPreference: ...

    async def clear_preference(self, app_user_id: uuid.UUID) -> None: ...
