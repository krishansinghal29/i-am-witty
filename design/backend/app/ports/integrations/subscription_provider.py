from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.models.entitlement import SubscriptionStatus


@dataclass(frozen=True)
class ProviderEntitlement:
    """Provider-reported entitlement, normalized so the backend can mirror it.

    The backend treats the provider (RevenueCat today) as the source of
    subscription truth and persists a derived `Entitlement` from this.
    """

    entitlement_key: str
    status: SubscriptionStatus
    product_id: str | None
    current_period_started_at: datetime | None
    current_period_ends_at: datetime | None
    trial_ends_at: datetime | None
    raw: dict


@dataclass(frozen=True)
class WebhookEvent:
    """A verified, normalized subscription webhook event."""

    event_id: str
    event_type: str
    revenuecat_app_user_id: str | None
    entitlement_key: str | None
    product_id: str | None
    purchased_at: datetime | None
    expires_at: datetime | None
    payload: dict


class SubscriptionProvider(Protocol):
    """Swappable subscription provider (RevenueCat today).

    RevenueCat is the source of subscription truth; the backend mirrors it via
    `get_entitlements` (pull) and `parse_webhook` (push). Keeping the vendor
    behind this port lets the infrastructure layer swap providers without
    changing `EntitlementService`.
    """

    async def get_entitlements(
        self, revenuecat_app_user_id: str
    ) -> list[ProviderEntitlement]:
        ...

    def parse_webhook(self, headers: dict, body: bytes) -> WebhookEvent:
        """Verify and parse a raw webhook request into a normalized event.

        Synchronous: signature verification and decoding are CPU-bound and
        must not depend on network or database access.
        """
        ...
