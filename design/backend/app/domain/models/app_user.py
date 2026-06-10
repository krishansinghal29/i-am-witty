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
