from __future__ import annotations

import uuid
from typing import Protocol

from app.domain.models.app_user import AppUser


class UserRepository(Protocol):
    async def find_by_id(self, app_user_id: uuid.UUID) -> AppUser | None: ...

    async def find_by_firebase_uid(self, firebase_uid: str) -> AppUser | None: ...

    async def create_authenticated_user(
        self, firebase_uid: str, timezone: str, locale: str | None = None
    ) -> AppUser:
        """Create a Firebase-authenticated user (status=active)."""
        ...

    async def touch_last_seen(self, app_user_id: uuid.UUID) -> None: ...
