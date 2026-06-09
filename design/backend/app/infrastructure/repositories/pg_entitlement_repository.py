from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.entitlement import (
    AccessState,
    Entitlement,
    SubscriptionStatus,
)
from app.infrastructure.db.orm.billing import (
    RevenueCatCustomer,
    SubscriptionEntitlement,
)
from app.infrastructure.db.orm.billing import (
    SubscriptionStatus as OrmSubscriptionStatus,
)


class PgEntitlementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_access_state(self, app_user_id: uuid.UUID) -> AccessState:
        stmt = select(SubscriptionEntitlement).where(
            SubscriptionEntitlement.app_user_id == app_user_id
        )
        result = await self._session.execute(stmt)
        entitlements = tuple(
            self._to_entitlement(row) for row in result.scalars().all()
        )
        is_riffy_plus = any(e.grants_access for e in entitlements)
        return AccessState(
            app_user_id=app_user_id,
            is_riffy_plus=is_riffy_plus,
            entitlements=entitlements,
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

    async def get_revenuecat_app_user_id(
        self, app_user_id: uuid.UUID
    ) -> str | None:
        row = await self._session.get(RevenueCatCustomer, app_user_id)
        return row.revenuecat_app_user_id if row is not None else None

    async def link_revenuecat_customer(
        self, app_user_id: uuid.UUID, revenuecat_app_user_id: str
    ) -> None:
        row = await self._session.get(RevenueCatCustomer, app_user_id)
        if row is None:
            row = RevenueCatCustomer(app_user_id=app_user_id)
            self._session.add(row)
        row.revenuecat_app_user_id = revenuecat_app_user_id
        row.updated_at = datetime.now(timezone.utc)
        await self._session.flush()

    @staticmethod
    def _to_entitlement(row: SubscriptionEntitlement) -> Entitlement:
        return Entitlement(
            entitlement_key=row.entitlement_key,
            status=SubscriptionStatus(row.status.value),
            product_id=row.product_id,
            current_period_ends_at=row.current_period_ends_at,
            trial_ends_at=row.trial_ends_at,
        )
