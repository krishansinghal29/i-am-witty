from __future__ import annotations

import uuid
from datetime import datetime
from typing import Protocol

from app.domain.models.entitlement import AccessState, Entitlement, ManualPremiumGrant


class EntitlementRepository(Protocol):
    async def get_access_state(self, app_user_id: uuid.UUID) -> AccessState: ...

    async def upsert_entitlement(
        self, app_user_id: uuid.UUID, entitlement: Entitlement, raw_snapshot: dict
    ) -> None: ...

    async def create_manual_grant(
        self,
        *,
        app_user_id: uuid.UUID,
        entitlement_key: str,
        starts_at: datetime,
        expires_at: datetime,
        granted_by: str | None = None,
        reason: str | None = None,
        metadata: dict | None = None,
    ) -> ManualPremiumGrant: ...

    async def revoke_manual_grant(
        self, grant_id: uuid.UUID, revoked_at: datetime
    ) -> ManualPremiumGrant | None: ...

    async def list_manual_grants(
        self, app_user_id: uuid.UUID
    ) -> tuple[ManualPremiumGrant, ...]: ...
