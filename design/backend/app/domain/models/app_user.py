from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    guest = "guest"
    active = "active"
    disabled = "disabled"
    deleted = "deleted"


@dataclass(frozen=True)
class AppUser:
    id: uuid.UUID
    firebase_uid: str | None
    status: UserStatus
    timezone: str
    locale: str | None
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime | None
    deleted_at: datetime | None

    @property
    def is_guest(self) -> bool:
        """True before the durable user is linked to a Firebase identity.

        A user is treated as a guest while either signal holds: no linked
        `firebase_uid` (the row was created for an anonymous session) or an
        explicit `guest` status. Both are checked so a half-linked row is never
        mistaken for an authenticated user.
        """
        return self.firebase_uid is None or self.status is UserStatus.guest
