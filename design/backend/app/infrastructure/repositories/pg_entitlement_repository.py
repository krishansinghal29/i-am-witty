from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.entitlement import (
    AccessState,
    Entitlement,
    ManualPremiumGrant,
    SubscriptionStatus,
)
from app.infrastructure.db.orm.billing import ManualPremiumGrant as OrmManualPremiumGrant
from app.infrastructure.db.orm.billing import SubscriptionEntitlement
from app.infrastructure.db.orm.billing import (
    SubscriptionStatus as OrmSubscriptionStatus,
)


class PgEntitlementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_access_state(self, app_user_id: uuid.UUID) -> AccessState:
        ent_stmt = select(SubscriptionEntitlement).where(
            SubscriptionEntitlement.app_user_id == app_user_id
        )
        ent_result = await self._session.execute(ent_stmt)
        entitlements = tuple(
            self._to_entitlement(row) for row in ent_result.scalars().all()
        )

        grant_stmt = select(OrmManualPremiumGrant).where(
            OrmManualPremiumGrant.app_user_id == app_user_id
        )
        grant_result = await self._session.execute(grant_stmt)
        manual_grants = tuple(
            self._to_manual_grant(row) for row in grant_result.scalars().all()
        )

        now = datetime.now(timezone.utc)
        is_riffy_plus = any(e.grants_access for e in entitlements) or any(
            g.grants_access(now) for g in manual_grants
        )
        return AccessState(
            app_user_id=app_user_id,
            is_riffy_plus=is_riffy_plus,
            entitlements=entitlements,
            manual_grants=manual_grants,
        )

    async def upsert_entitlement(
        self, app_user_id: uuid.UUID, entitlement: Entitlement, raw_snapshot: dict
    ) -> None:
        stmt = select(SubscriptionEntitlement).where(
            SubscriptionEntitlement.app_user_id == app_user_id,
            SubscriptionEntitlement.entitlement_key == entitlement.entitlement_key,
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        if row is None:
            row = SubscriptionEntitlement(
                app_user_id=app_user_id,
                entitlement_key=entitlement.entitlement_key,
            )
            self._session.add(row)
        row.status = OrmSubscriptionStatus(entitlement.status.value)
        row.product_id = entitlement.product_id
        row.current_period_ends_at = entitlement.current_period_ends_at
        row.trial_ends_at = entitlement.trial_ends_at
        row.last_synced_at = datetime.now(timezone.utc)
        row.raw_snapshot = raw_snapshot
        await self._session.flush()

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
    ) -> ManualPremiumGrant:
        row = OrmManualPremiumGrant(
            app_user_id=app_user_id,
            entitlement_key=entitlement_key,
            starts_at=starts_at,
            expires_at=expires_at,
            granted_by=granted_by,
            reason=reason,
            grant_metadata=metadata or {},
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_manual_grant(row)

    async def revoke_manual_grant(
        self, grant_id: uuid.UUID, revoked_at: datetime
    ) -> ManualPremiumGrant | None:
        row = await self._session.get(OrmManualPremiumGrant, grant_id)
        if row is None:
            return None
        row.revoked_at = revoked_at
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_manual_grant(row)

    async def list_manual_grants(
        self, app_user_id: uuid.UUID
    ) -> tuple[ManualPremiumGrant, ...]:
        stmt = (
            select(OrmManualPremiumGrant)
            .where(OrmManualPremiumGrant.app_user_id == app_user_id)
            .order_by(OrmManualPremiumGrant.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return tuple(self._to_manual_grant(row) for row in result.scalars().all())

    @staticmethod
    def _to_entitlement(row: SubscriptionEntitlement) -> Entitlement:
        return Entitlement(
            entitlement_key=row.entitlement_key,
            status=SubscriptionStatus(row.status.value),
            product_id=row.product_id,
            current_period_ends_at=row.current_period_ends_at,
            trial_ends_at=row.trial_ends_at,
        )

    @staticmethod
    def _to_manual_grant(row: OrmManualPremiumGrant) -> ManualPremiumGrant:
        return ManualPremiumGrant(
            id=row.id,
            entitlement_key=row.entitlement_key,
            starts_at=row.starts_at,
            expires_at=row.expires_at,
            revoked_at=row.revoked_at,
            granted_by=row.granted_by,
            reason=row.reason,
        )
