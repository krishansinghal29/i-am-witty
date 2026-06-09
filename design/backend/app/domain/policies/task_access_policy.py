from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.entitlement import AccessState
from app.domain.models.task import Task


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    requires_premium: bool
    reason: str | None


def evaluate_task_access(task: Task, access: AccessState) -> AccessDecision:
    """Decide whether a user may start a task given its access tier.

    Free tasks are always allowed. Premium tasks require an active Riffy+
    entitlement (`access.is_riffy_plus`); what counts as "active" is resolved
    in the entitlement model, so this policy stays a pure tier check.
    """
    if not task.requires_premium:
        return AccessDecision(allowed=True, requires_premium=False, reason=None)
    if access.is_riffy_plus:
        return AccessDecision(allowed=True, requires_premium=True, reason=None)
    return AccessDecision(
        allowed=False,
        requires_premium=True,
        reason="premium_required",
    )
