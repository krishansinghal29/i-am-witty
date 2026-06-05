from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class FeatureGate:
    feature_key: str
    default_enabled: bool
    requires_entitlement: str | None = None
    min_app_version: str | None = None


@dataclass(frozen=True)
class PublicConfig:
    values: dict = field(default_factory=dict)
    free_task_limit: int = 0
    feature_gates: tuple[FeatureGate, ...] = ()


class ConfigRepository(Protocol):
    async def get_public_config(self) -> PublicConfig:
        """Assemble the client-facing config payload (public values + gates)."""
        ...

    async def get_value(self, key: str) -> dict | None:
        """Return the raw jsonb value stored for a single config key."""
        ...

    async def get_free_task_limit(self) -> int: ...

    async def get_feature_gates(self) -> list[FeatureGate]: ...
