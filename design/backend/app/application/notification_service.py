from __future__ import annotations

import uuid

from app.application.unit_of_work import UnitOfWork
from app.ports.repositories.notification_device_repository import (
    NotificationDeviceRecord,
    NotificationDeviceRepository,
    RegisterDeviceInput,
)


class NotificationService:
    def __init__(
        self, devices: NotificationDeviceRepository, uow: UnitOfWork
    ) -> None:
        self._devices = devices
        self._uow = uow

    async def register_device(
        self, input: RegisterDeviceInput
    ) -> NotificationDeviceRecord:
        async with self._uow.transaction():
            return await self._devices.register_device(input)

    async def disable_device(
        self, app_user_id: uuid.UUID, device_key: str
    ) -> None:
        async with self._uow.transaction():
            await self._devices.disable_device(app_user_id, device_key)
