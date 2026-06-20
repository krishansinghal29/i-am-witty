"""Shared helpers for OutcomeRule implementations. [P3b]

Quality scaling is the key idea: a GOOD move lands full; MEDIOCRE lands half; a
BOTCHED move flips the intended positive into a small penalty (a botched tease is
an insult, a botched cold-read is creepy, etc.).
"""
from __future__ import annotations

from roleplay_sim.domain.enums import Consequence, Quality
from roleplay_sim.domain.models import OutcomeResult, StateDelta

QMUL: dict[Quality, float] = {Quality.GOOD: 1.0, Quality.MEDIOCRE: 0.5, Quality.BOTCHED: -0.6}


def scale(quality: Quality, **emotional: float) -> dict[str, float]:
    """Scale a dict of intended-positive emotional deltas by move quality."""
    m = QMUL[quality]
    return {k: round(v * m, 3) for k, v in emotional.items()}


def outcome(
    emotional: dict[str, float] | None = None,
    *,
    flags: dict | None = None,
    consequences: list[Consequence] | None = None,
    success: bool | None = None,
    notes: str = "",
) -> OutcomeResult:
    return OutcomeResult(
        delta=StateDelta(emotional=emotional or {}, flags=flags or {}),
        consequences=consequences or [],
        success=success,
        notes=notes,
    )
