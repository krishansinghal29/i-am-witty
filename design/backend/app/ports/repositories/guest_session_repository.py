from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class GuestSessionRecord:
    id: uuid.UUID
    app_user_id: uuid.UUID
    session_token_hash: str
    created_at: datetime
    last_seen_at: datetime | None
    expires_at: datetime | None
    converted_at: datetime | None


class GuestSessionRepository(Protocol):
    async def create_session(
        self,
        app_user_id: uuid.UUID,
        session_token_hash: str,
        expires_at: datetime | None = None,
    ) -> GuestSessionRecord: ...

    async def find_by_token_hash(
        self, session_token_hash: str
    ) -> GuestSessionRecord | None: ...

    async def touch_last_seen(self, session_id: uuid.UUID) -> None: ...

    async def mark_converted(self, session_id: uuid.UUID) -> None:
        """Record that the guest session was linked to an authenticated user."""
        ...
