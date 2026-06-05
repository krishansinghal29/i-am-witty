from __future__ import annotations

from typing import Protocol


class Analytics(Protocol):
    """Vendor-neutral analytics + feature-flag port (PostHog-shaped today).

    PostHog is used for product analytics and experimentation flags only.
    Backend-enforced access gates live in `feature_gate_defaults` and must not
    be driven by `is_feature_enabled`; treat flags here as experimentation
    toggles, never as authoritative entitlement checks.
    """

    def capture(
        self, app_user_id: str, event: str, properties: dict | None = None
    ) -> None:
        ...

    def identify(self, app_user_id: str, traits: dict | None = None) -> None:
        ...

    def is_feature_enabled(self, flag: str, app_user_id: str) -> bool:
        ...
