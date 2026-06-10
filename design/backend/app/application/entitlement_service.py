from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.application.exceptions import NotFoundError, ValidationError
from app.application.unit_of_work import UnitOfWork
from app.domain.models.entitlement import AccessState, Entitlement, ManualPremiumGrant
from app.ports.integrations.subscription_provider import (
    ProviderEntitlement,
    SubscriptionProvider,
    WebhookEvent,
)
from app.ports.repositories.entitlement_repository import EntitlementRepository
from app.ports.repositories.user_repository import UserRepository


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


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

    async def grant_manual_premium(
        self,
        *,
        app_user_id: uuid.UUID,
        expires_at: datetime,
        entitlement_key: str = "riffy_plus",
        starts_at: datetime | None = None,
        granted_by: str | None = None,
        reason: str | None = None,
        metadata: dict | None = None,
    ) -> ManualPremiumGrant:
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")

        starts_at = _as_aware_utc(starts_at or datetime.now(timezone.utc))
        expires_at = _as_aware_utc(expires_at)
        if expires_at <= starts_at:
            raise ValidationError("grant_expiry_must_be_after_start")

        async with self._uow.transaction():
            return await self._entitlements.create_manual_grant(
                app_user_id=app_user_id,
                entitlement_key=entitlement_key,
                starts_at=starts_at,
                expires_at=expires_at,
                granted_by=granted_by,
                reason=reason,
                metadata=metadata,
            )

    async def revoke_manual_premium_grant(
        self, grant_id: uuid.UUID
    ) -> ManualPremiumGrant:
        async with self._uow.transaction():
            grant = await self._entitlements.revoke_manual_grant(
                grant_id, datetime.now(timezone.utc)
            )
            if grant is None:
                raise NotFoundError("manual_grant_not_found")
            return grant

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
