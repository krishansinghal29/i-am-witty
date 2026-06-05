from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class UserProfileRecord:
    app_user_id: uuid.UUID
    display_name: str | None
    created_at: datetime
    updated_at: datetime


class ProfileRepository(Protocol):
    async def get_profile(self, app_user_id: uuid.UUID) -> UserProfileRecord | None: ...

    async def upsert_profile(
        self, app_user_id: uuid.UUID, display_name: str | None
    ) -> UserProfileRecord: ...
