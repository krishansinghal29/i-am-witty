from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class SubscriptionStatus(str, Enum):
    active = "active"
    trialing = "trialing"
    past_due = "past_due"
    canceled = "canceled"
    expired = "expired"
    unknown = "unknown"


# active/trialing are the only states that currently grant paid access; a
# trialing user has full access until the trial converts or lapses.
_ACCESS_GRANTING_STATUSES = frozenset(
    {SubscriptionStatus.active, SubscriptionStatus.trialing}
)


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class Entitlement:
    entitlement_key: str
    status: SubscriptionStatus
    product_id: str | None
    current_period_ends_at: datetime | None
    trial_ends_at: datetime | None

    @property
    def grants_access(self) -> bool:
        return self.status in _ACCESS_GRANTING_STATUSES


@dataclass(frozen=True)
class ManualPremiumGrant:
    id: uuid.UUID
    entitlement_key: str
    starts_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    granted_by: str | None
    reason: str | None

    def grants_access(self, now: datetime | None = None) -> bool:
        now = _as_aware_utc(now or datetime.now(timezone.utc))
        starts_at = _as_aware_utc(self.starts_at)
        expires_at = _as_aware_utc(self.expires_at)
        return starts_at <= now < expires_at and self.revoked_at is None


@dataclass(frozen=True)
class AccessState:
    app_user_id: uuid.UUID
    is_riffy_plus: bool
    entitlements: tuple[Entitlement, ...] = ()
    manual_grants: tuple[ManualPremiumGrant, ...] = ()

    @staticmethod
    def status_grants_access(status: SubscriptionStatus) -> bool:
        """Whether a raw subscription status grants paid access.

        Centralizes the active/trialing rule so policies and repositories
        derive `is_riffy_plus` consistently instead of re-checking enum members.
        """
        return status in _ACCESS_GRANTING_STATUSES

    @property
    def has_active_entitlement(self) -> bool:
        """True if any mirrored entitlement is in an access-granting state."""
        return any(e.grants_access for e in self.entitlements)

    @property
    def has_active_manual_grant(self) -> bool:
        """True if any manual grant is active at the time of evaluation."""
        now = datetime.now(timezone.utc)
        return any(g.grants_access(now) for g in self.manual_grants)
