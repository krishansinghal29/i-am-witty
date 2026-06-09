from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
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
class AccessState:
    app_user_id: uuid.UUID
    is_riffy_plus: bool
    entitlements: tuple[Entitlement, ...] = ()

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
