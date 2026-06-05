from __future__ import annotations

import uuid

from app.application.unit_of_work import UnitOfWork
from app.domain.models.entitlement import AccessState, Entitlement, SubscriptionStatus
from app.ports.integrations.subscription_provider import (
    ProviderEntitlement,
    SubscriptionProvider,
)
from app.ports.repositories.entitlement_repository import EntitlementRepository


class EntitlementService:
    """Mirrors provider subscription truth and exposes derived access state."""

    def __init__(
        self,
        entitlements: EntitlementRepository,
        provider: SubscriptionProvider,
        uow: UnitOfWork,
    ) -> None:
        self._entitlements = entitlements
        self._provider = provider
        self._uow = uow

    async def get_access_state(self, app_user_id: uuid.UUID) -> AccessState:
        return await self._entitlements.get_access_state(app_user_id)

    async def link_customer(
        self, app_user_id: uuid.UUID, revenuecat_app_user_id: str
    ) -> None:
        async with self._uow.transaction():
            await self._entitlements.link_revenuecat_customer(
                app_user_id, revenuecat_app_user_id
            )

    async def sync_from_provider(self, app_user_id: uuid.UUID) -> AccessState:
        rc_id = await self._entitlements.get_revenuecat_app_user_id(app_user_id)
        if rc_id is None:
            return await self._entitlements.get_access_state(app_user_id)
        provider_ents = await self._provider.get_entitlements(rc_id)
        async with self._uow.transaction():
            for pe in provider_ents:
                await self._entitlements.upsert_entitlement(
                    app_user_id,
                    Entitlement(
                        entitlement_key=pe.entitlement_key,
                        status=pe.status,
                        product_id=pe.product_id,
                        current_period_ends_at=pe.current_period_ends_at,
                        trial_ends_at=pe.trial_ends_at,
                    ),
                    raw_snapshot=pe.raw,
                )
        return await self._entitlements.get_access_state(app_user_id)
