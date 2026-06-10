from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class CreateSupportMessageInput:
    message_text: str
    app_user_id: uuid.UUID | None = None
    source_screen: str | None = None


@dataclass(frozen=True)
class SupportMessageRecord:
    id: uuid.UUID
    app_user_id: uuid.UUID | None
    message_text: str
    status: str
    external_ticket_id: str | None
    delivery_error: str | None
    created_at: datetime


class SupportRepository(Protocol):
    async def create_message(
        self, input: CreateSupportMessageInput
    ) -> SupportMessageRecord: ...

    async def update_delivery_status(
        self,
        message_id: uuid.UUID,
        status: str,
        external_ticket_id: str | None = None,
        delivery_error: str | None = None,
    ) -> None: ...
