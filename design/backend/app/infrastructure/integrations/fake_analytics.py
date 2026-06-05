from __future__ import annotations


class FakeAnalytics:
    """No-op analytics sink that records calls in memory for test inspection.

    Feature flags always resolve to False: backend access gates come from the
    database (`feature_gate_defaults`), never from experimentation flags.
    """

    def __init__(self) -> None:
        self.events: list[tuple] = []

    def capture(
        self, app_user_id: str, event: str, properties: dict | None = None
    ) -> None:
        """Record a capture call."""
        self.events.append(("capture", app_user_id, event, properties or {}))

    def identify(self, app_user_id: str, traits: dict | None = None) -> None:
        """Record an identify call."""
        self.events.append(("identify", app_user_id, traits or {}))

    def is_feature_enabled(self, flag: str, app_user_id: str) -> bool:
        """Always False; flags are not authoritative entitlement checks."""
        return False
