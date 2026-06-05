from __future__ import annotations

import uuid

from app.application.exceptions import ValidationError
from app.application.unit_of_work import UnitOfWork
from app.ports.repositories.support_repository import (
    CreateSupportMessageInput,
    SupportMessageRecord,
    SupportRepository,
)


class SupportService:
    def __init__(self, support: SupportRepository, uow: UnitOfWork) -> None:
        self._support = support
        self._uow = uow

    async def submit_support(
        self,
        message_text: str,
        app_user_id: uuid.UUID | None = None,
        guest_session_id: uuid.UUID | None = None,
        source_screen: str | None = None,
    ) -> SupportMessageRecord:
        if not message_text or not message_text.strip():
            raise ValidationError("empty_message")
        async with self._uow.transaction():
            return await self._support.create_message(
                CreateSupportMessageInput(
                    message_text=message_text,
                    app_user_id=app_user_id,
                    guest_session_id=guest_session_id,
                    source_screen=source_screen,
                )
            )
