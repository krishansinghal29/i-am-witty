from __future__ import annotations

import uuid

from app.application.unit_of_work import UnitOfWork
from app.domain.models.entitlement import AccessState, Entitlement
from app.ports.integrations.subscription_provider import (
    ProviderEntitlement,
    SubscriptionProvider,
    WebhookEvent,
)
from app.ports.repositories.entitlement_repository import EntitlementRepository
from app.ports.repositories.user_repository import UserRepository


class EntitlementService:
    """Mirrors provider subscription truth and exposes derived access state."""

    def __init__(
        self,
        entitlements: EntitlementRepository,
        users: UserRepository,
        provider: SubscriptionProvider,
        uow: UnitOfWork,
    ) -> None:
        self._entitlements = entitlements
        self._users = users
        self._provider = provider
        self._uow = uow

    async def get_access_state(self, app_user_id: uuid.UUID) -> AccessState:
        return await self._entitlements.get_access_state(app_user_id)

    async def sync_from_provider(self, app_user_id: uuid.UUID) -> AccessState:
        """Pull the subscriber from RevenueCat now and mirror it.

        Option A: the RevenueCat app user id IS our ``app_user_id`` (a UUID) --
        the same identity the webhook path matches on. This lets the client
        reconcile immediately after a purchase instead of waiting on the
        (eventually-consistent) webhook. The upsert is idempotent, so calling
        this repeatedly is safe.
        """
        provider_ents = await self._provider.get_entitlements(str(app_user_id))
        await self._apply(app_user_id, provider_ents)
        return await self._entitlements.get_access_state(app_user_id)

    async def process_webhook(self, event: WebhookEvent) -> None:
        """Mirror a verified RevenueCat webhook onto our stored entitlements.

        Option A: RevenueCat's app user id IS our ``app_user_id`` (a UUID). We
        re-fetch the subscriber from RevenueCat rather than trusting the event
        body -- that is the authoritative current state and makes redelivered
        webhooks idempotent. Events whose id is missing, not a UUID, or unknown
        to us are ignored (a no-op, still acked at the edge).
        """
        rc_id = event.revenuecat_app_user_id
        if not rc_id:
            return
        try:
            app_user_id = uuid.UUID(rc_id)
        except ValueError:
            return
        if await self._users.find_by_id(app_user_id) is None:
            return
        provider_ents = await self._provider.get_entitlements(rc_id)
        await self._apply(app_user_id, provider_ents)

    async def _apply(
        self, app_user_id: uuid.UUID, provider_ents: list[ProviderEntitlement]
    ) -> None:
        """Persist the provider's entitlements for a user in one transaction."""
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
