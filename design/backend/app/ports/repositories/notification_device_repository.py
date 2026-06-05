from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class RegisterDeviceInput:
    app_user_id: uuid.UUID
    device_key: str
    platform: str
    push_token: str | None = None
    permission_status: str = "unknown"
    app_version: str | None = None
    release_channel: str | None = None


@dataclass(frozen=True)
class NotificationDeviceRecord:
    id: uuid.UUID
    app_user_id: uuid.UUID
    device_key: str
    platform: str
    push_token: str | None
    permission_status: str
    last_seen_at: datetime | None
    disabled_at: datetime | None


class NotificationDeviceRepository(Protocol):
    async def register_device(
        self, input: RegisterDeviceInput
    ) -> NotificationDeviceRecord:
        """Create or update the device row for (app_user, device_key)."""
        ...

    async def disable_device(self, app_user_id: uuid.UUID, device_key: str) -> None: ...
