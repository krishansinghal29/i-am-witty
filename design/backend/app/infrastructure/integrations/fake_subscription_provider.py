from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

from app.domain.models.entitlement import SubscriptionStatus
from app.ports.integrations.subscription_provider import (
    ProviderEntitlement,
    WebhookEvent,
)


class FakeSubscriptionProvider:
    """Deterministic stand-in for the real (RevenueCat) subscription provider.

    Entitlements are derived from the app-user id: ids containing "premium"
    are treated as paid, everything else as free. No network, no SDK, no
    signature verification.
    """

    async def get_entitlements(
        self, revenuecat_app_user_id: str
    ) -> list[ProviderEntitlement]:
        """Return one active entitlement for "premium"-tagged ids, else none."""
        if "premium" not in revenuecat_app_user_id:
            return []
        now = datetime.now(timezone.utc)
        return [
            ProviderEntitlement(
                entitlement_key="witty_plus",
                status=SubscriptionStatus.active,
                product_id="witty_plus_monthly",
                current_period_started_at=now,
                current_period_ends_at=now + timedelta(days=30),
                trial_ends_at=None,
                raw={"source": "fake"},
            )
        ]

    def parse_webhook(self, headers: dict, body: bytes) -> WebhookEvent:
        """Parse a raw webhook body defensively (no signature check)."""
        raw_body = body or b"{}"
        try:
            payload = json.loads(raw_body)
        except (ValueError, TypeError):
            payload = {}
        if not isinstance(payload, dict):
            payload = {}

        event_id = payload.get("id") or payload.get("event_id")
        if not event_id:
            event_id = hashlib.sha256(raw_body).hexdigest()

        return WebhookEvent(
            event_id=str(event_id),
            event_type=payload.get("type")
            or payload.get("event_type")
            or "unknown",
            revenuecat_app_user_id=payload.get("app_user_id"),
            entitlement_key=payload.get("entitlement_key")
            or payload.get("entitlement_id"),
            product_id=payload.get("product_id"),
            purchased_at=self._parse_dt(payload.get("purchased_at")),
            expires_at=self._parse_dt(payload.get("expires_at")),
            payload=payload,
        )

    @staticmethod
    def _parse_dt(value: object) -> datetime | None:
        """Best-effort ISO-8601 parse; never raises on malformed input."""
        if not isinstance(value, str) or not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
