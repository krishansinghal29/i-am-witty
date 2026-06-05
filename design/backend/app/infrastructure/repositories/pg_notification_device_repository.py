from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.comms import NotificationDevice as OrmNotificationDevice
from app.infrastructure.db.orm.comms import NotificationPermissionStatus
from app.ports.repositories.notification_device_repository import (
    NotificationDeviceRecord,
    NotificationDeviceRepository,
    RegisterDeviceInput,
)


class PgNotificationDeviceRepository(NotificationDeviceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register_device(
        self, input: RegisterDeviceInput
    ) -> NotificationDeviceRecord:
        row = await self._get(input.app_user_id, input.device_key)
        if row is None:
            row = OrmNotificationDevice(
                app_user_id=input.app_user_id,
                device_key=input.device_key,
                platform=input.platform,
            )
            self._session.add(row)
        row.platform = input.platform
        row.push_token = input.push_token
        row.permission_status = NotificationPermissionStatus(input.permission_status)
        row.app_version = input.app_version
        row.release_channel = input.release_channel
        row.last_seen_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_dto(row)

    async def disable_device(self, app_user_id: uuid.UUID, device_key: str) -> None:
        row = await self._get(app_user_id, device_key)
        if row is not None:
            row.disabled_at = datetime.now(timezone.utc)
            await self._session.flush()

    async def _get(
        self, app_user_id: uuid.UUID, device_key: str
    ) -> OrmNotificationDevice | None:
        stmt = select(OrmNotificationDevice).where(
            OrmNotificationDevice.app_user_id == app_user_id,
            OrmNotificationDevice.device_key == device_key,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def _to_dto(row: OrmNotificationDevice) -> NotificationDeviceRecord:
        return NotificationDeviceRecord(
            id=row.id,
            app_user_id=row.app_user_id,
            device_key=row.device_key,
            platform=row.platform,
            push_token=row.push_token,
            permission_status=row.permission_status.value,
            last_seen_at=row.last_seen_at,
            disabled_at=row.disabled_at,
        )
