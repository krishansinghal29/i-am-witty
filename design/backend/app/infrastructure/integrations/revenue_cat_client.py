from __future__ import annotations

import hmac
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import httpx

from app.domain.models.entitlement import SubscriptionStatus
from app.ports.integrations.subscription_provider import (
    ProviderEntitlement,
    WebhookEvent,
)

if TYPE_CHECKING:
    from app.settings import Settings

_API_BASE_URL = "https://api.revenuecat.com/v1"
_TRIAL_PERIOD_TYPES = frozenset({"trial", "intro"})


class RevenueCatSubscriptionProvider:
    """Real RevenueCat adapter for the `SubscriptionProvider` port.

    RevenueCat is the source of subscription truth. State is mirrored by pulling
    the subscriber via the v1 REST API (`get_entitlements`) and by consuming
    dashboard-configured webhooks (`parse_webhook`). RevenueCat does not sign
    webhooks, so the only authenticity check is the shared `Authorization`
    header value configured in the dashboard.
    """

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.revenuecat_api_key
        self._webhook_auth = settings.revenuecat_webhook_auth
        # Lazy client keeps the module importable without credentials and avoids
        # opening a connection pool until the first real request.
        self._client: httpx.AsyncClient | None = None

    def _require_key(self) -> str:
        if not self._api_key:
            raise RuntimeError("revenuecat_not_configured")
        return self._api_key

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=_API_BASE_URL, timeout=10.0)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get_entitlements(
        self, revenuecat_app_user_id: str
    ) -> list[ProviderEntitlement]:
        """Fetch and normalize the subscriber's entitlements from RevenueCat.

        An unknown subscriber (404) is treated as "no entitlements" rather than
        an error, so callers can mirror the absence of paid access.
        """
        api_key = self._require_key()
        client = self._get_client()
        response = await client.get(
            f"/subscribers/{revenuecat_app_user_id}",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code == 404:
            return []
        response.raise_for_status()

        subscriber = (response.json() or {}).get("subscriber") or {}
        entitlements = subscriber.get("entitlements") or {}
        subscriptions = subscriber.get("subscriptions") or {}
        now = datetime.now(timezone.utc)

        result: list[ProviderEntitlement] = []
        for key, entitlement in entitlements.items():
            if not isinstance(entitlement, dict):
                continue
            product_id = entitlement.get("product_identifier")
            subscription = subscriptions.get(product_id)
            subscription = subscription if isinstance(subscription, dict) else {}

            period_started = self._to_datetime(entitlement.get("purchase_date"))
            period_ends = self._to_datetime(entitlement.get("expires_date"))
            grace_ends = self._to_datetime(
                entitlement.get("grace_period_expires_date")
            ) or self._to_datetime(subscription.get("grace_period_expires_date"))
            is_trial = (
                str(subscription.get("period_type") or "").lower()
                in _TRIAL_PERIOD_TYPES
            )
            status = self._derive_status(
                expires_at=period_ends,
                grace_at=grace_ends,
                expiry_present="expires_date" in entitlement,
                is_trial=is_trial,
                now=now,
            )
            result.append(
                ProviderEntitlement(
                    entitlement_key=str(key),
                    status=status,
                    product_id=product_id,
                    current_period_started_at=period_started,
                    current_period_ends_at=period_ends,
                    trial_ends_at=period_ends if is_trial else None,
                    raw=entitlement,
                )
            )
        return result

    def parse_webhook(self, headers: dict, body: bytes) -> WebhookEvent:
        """Verify the shared secret and normalize a RevenueCat webhook.

        Synchronous by contract: verification and decoding are CPU-bound and must
        not touch the network or database.
        """
        if self._webhook_auth:
            provided = self._authorization_header(headers)
            if not hmac.compare_digest(self._webhook_auth, provided):
                raise PermissionError("invalid_webhook_auth")

        try:
            payload = json.loads(body or b"{}")
        except (ValueError, TypeError):
            payload = {}
        if not isinstance(payload, dict):
            payload = {}

        event = payload.get("event")
        event = event if isinstance(event, dict) else {}

        return WebhookEvent(
            event_id=str(event.get("id") or ""),
            event_type=str(event.get("type") or "unknown"),
            revenuecat_app_user_id=event.get("app_user_id"),
            entitlement_key=self._first_entitlement(event),
            product_id=event.get("product_id"),
            purchased_at=self._to_datetime(event.get("purchased_at_ms")),
            expires_at=self._to_datetime(event.get("expiration_at_ms")),
            payload=payload,
        )

    @staticmethod
    def _authorization_header(headers: dict) -> str:
        """Case-insensitive lookup of the `Authorization` header value."""
        for name, value in (headers or {}).items():
            if isinstance(name, str) and name.lower() == "authorization":
                return value if isinstance(value, str) else ""
        return ""

    @staticmethod
    def _first_entitlement(event: dict) -> str | None:
        """RevenueCat sends `entitlement_ids` (array); older events `entitlement_id`."""
        ids = event.get("entitlement_ids")
        if isinstance(ids, (list, tuple)):
            return str(ids[0]) if ids else None
        if isinstance(ids, str) and ids:
            return ids
        single = event.get("entitlement_id")
        return single if isinstance(single, str) and single else None

    @staticmethod
    def _derive_status(
        *,
        expires_at: datetime | None,
        grace_at: datetime | None,
        expiry_present: bool,
        is_trial: bool,
        now: datetime,
    ) -> SubscriptionStatus:
        # A present-but-null expiry is a lifetime (non-expiring) entitlement.
        if expiry_present and expires_at is None and grace_at is None:
            return SubscriptionStatus.active

        active_until = expires_at
        if grace_at is not None and (active_until is None or grace_at > active_until):
            active_until = grace_at

        if active_until is not None and active_until > now:
            in_grace = (
                grace_at is not None
                and grace_at > now
                and (expires_at is None or expires_at <= now)
            )
            if is_trial or in_grace:
                return SubscriptionStatus.trialing
            return SubscriptionStatus.active
        return SubscriptionStatus.expired

    @staticmethod
    def _to_datetime(value: object) -> datetime | None:
        """Normalize epoch-ms ints or ISO-8601 strings to aware UTC datetimes."""
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            if text.isdigit():
                return datetime.fromtimestamp(int(text) / 1000, tz=timezone.utc)
            try:
                return datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None
