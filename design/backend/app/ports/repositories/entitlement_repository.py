from __future__ import annotations

import uuid
from typing import Protocol

from app.domain.models.entitlement import AccessState, Entitlement


class EntitlementRepository(Protocol):
    async def get_access_state(self, app_user_id: uuid.UUID) -> AccessState: ...

    async def upsert_entitlement(
        self, app_user_id: uuid.UUID, entitlement: Entitlement, raw_snapshot: dict
    ) -> None: ...

    async def get_revenuecat_app_user_id(
        self, app_user_id: uuid.UUID
    ) -> str | None: ...

    async def link_revenuecat_customer(
        self, app_user_id: uuid.UUID, revenuecat_app_user_id: str
    ) -> None: ...
