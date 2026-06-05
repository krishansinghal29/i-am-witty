from __future__ import annotations

import uuid
from typing import Protocol

from app.domain.models.app_user import AppUser


class UserRepository(Protocol):
    async def find_by_id(self, app_user_id: uuid.UUID) -> AppUser | None: ...

    async def find_by_firebase_uid(self, firebase_uid: str) -> AppUser | None: ...

    async def create_guest_user(
        self, timezone: str, locale: str | None = None
    ) -> AppUser: ...

    async def link_firebase_uid(
        self, app_user_id: uuid.UUID, firebase_uid: str
    ) -> AppUser:
        """Attach a Firebase identity to an existing guest user (guest→authenticated)."""
        ...

    async def touch_last_seen(self, app_user_id: uuid.UUID) -> None: ...
