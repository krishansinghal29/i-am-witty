"""State clamping + StateDelta application helpers. [P3]"""
from __future__ import annotations

from roleplay_sim.domain.models import GameState, LadderState, StateDelta


def clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def clamp_level(v: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, v))


def normalize_ladder(ls: LadderState) -> None:
    """Enforce ladder invariants in place.

    - levels in [0, 10]
    - ceiling >= reached (an accepted rung stays available)…
    - …unless a lock caps the ceiling below it (point-of-no-return).
    """
    ls.reached = clamp_level(ls.reached)
    ls.ceiling = clamp_level(ls.ceiling)
    if ls.locked is not None:
        ls.locked = int(clamp_level(ls.locked))
        cap = max(0.0, ls.locked - 1.0)
        ls.ceiling = min(ls.ceiling, cap)
    else:
        ls.ceiling = max(ls.ceiling, ls.reached)


def apply_delta(state: GameState, delta: StateDelta) -> None:
    """Apply an aggregated delta to `state` in place, then clamp/normalize."""
    e = state.emotional
    for k, v in delta.emotional.items():
        if hasattr(e, k):
            setattr(e, k, clamp(getattr(e, k) + v))

    for lad, dv in delta.ladder_ceiling.items():
        state.ladders[lad].ceiling = clamp_level(state.ladders[lad].ceiling + dv)
    for lad, val in delta.ladder_reached.items():
        ls = state.ladders[lad]
        ls.reached = clamp_level(max(ls.reached, val))
    for lad, rung in delta.lock.items():
        ls = state.ladders[lad]
        ls.locked = rung if ls.locked is None else min(ls.locked, rung)

    for k, val in delta.flags.items():
        if hasattr(state.flags, k):
            setattr(state.flags, k, val)

    for ls in state.ladders.values():
        normalize_ladder(ls)
