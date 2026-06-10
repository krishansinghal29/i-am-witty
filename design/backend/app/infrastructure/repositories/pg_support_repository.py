from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.comms import SupportMessage as OrmSupportMessage
from app.infrastructure.db.orm.comms import SupportMessageStatus
from app.ports.repositories.support_repository import (
    CreateSupportMessageInput,
    SupportMessageRecord,
    SupportRepository,
)


class PgSupportRepository(SupportRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_message(
        self, input: CreateSupportMessageInput
    ) -> SupportMessageRecord:
        row = OrmSupportMessage(
            app_user_id=input.app_user_id,
            source_screen=input.source_screen,
            message_text=input.message_text,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_dto(row)

    async def update_delivery_status(
        self,
        message_id: uuid.UUID,
        status: str,
        external_ticket_id: str | None = None,
        delivery_error: str | None = None,
    ) -> None:
        row = await self._session.get(OrmSupportMessage, message_id)
        if row is None:
            return
        row.status = SupportMessageStatus(status)
        if external_ticket_id is not None:
            row.external_ticket_id = external_ticket_id
        if delivery_error is not None:
            row.delivery_error = delivery_error
        now = datetime.now(timezone.utc)
        if status == SupportMessageStatus.delivered.value:
            row.delivered_at = now
        elif status == SupportMessageStatus.closed.value:
            row.closed_at = now
        await self._session.flush()

    @staticmethod
    def _to_dto(row: OrmSupportMessage) -> SupportMessageRecord:
        return SupportMessageRecord(
            id=row.id,
            app_user_id=row.app_user_id,
            message_text=row.message_text,
            status=row.status.value,
            external_ticket_id=row.external_ticket_id,
            delivery_error=row.delivery_error,
            created_at=row.created_at,
        )
