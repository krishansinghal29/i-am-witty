from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.entitlement import AccessState

UNLIMITED_REMAINING = -1
"""Sentinel `remaining` value meaning "no free-task cap applies" (Witty+).

Using -1 rather than 0/None lets callers distinguish "unlimited" from "0 left"
without a separate flag, while keeping `remaining` a plain int.
"""


@dataclass(frozen=True)
class FreeLimitState:
    free_tasks_completed: int
    free_task_limit: int


@dataclass(frozen=True)
class FreeLimitDecision:
    allowed: bool
    should_paywall: bool
    remaining: int
    reason: str | None


def evaluate_free_limit(
    usage: FreeLimitState, access: AccessState
) -> FreeLimitDecision:
    """Enforce the non-subscriber free daily task cap (functional req §6).

    Witty+ users are unlimited: allowed, no paywall, and
    `remaining = UNLIMITED_REMAINING`. Non-subscribers are allowed while
    `free_tasks_completed < free_task_limit`; once the cap is reached they are
    blocked and the caller should surface the paywall. `remaining` is clamped
    at 0 so an over-count never reports a negative balance.
    """
    if access.is_witty_plus:
        return FreeLimitDecision(
            allowed=True,
            should_paywall=False,
            remaining=UNLIMITED_REMAINING,
            reason=None,
        )

    remaining = max(0, usage.free_task_limit - usage.free_tasks_completed)
    if usage.free_tasks_completed < usage.free_task_limit:
        return FreeLimitDecision(
            allowed=True,
            should_paywall=False,
            remaining=remaining,
            reason=None,
        )
    return FreeLimitDecision(
        allowed=False,
        should_paywall=True,
        remaining=remaining,
        reason="free_limit_reached",
    )
