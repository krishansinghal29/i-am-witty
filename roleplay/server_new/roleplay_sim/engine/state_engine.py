"""StateEngine.apply(): the deterministic per-turn state update. [P3]

Flow:
  1. deep-copy state (caller's state is never mutated)
  2. passive accrual (time-on-target raises comfort + ceilings)
  3. update fractionation counters from the turn's register
  4. for each move (then the action): OutcomeRule.resolve -> per-move Modifier chain
  5. resolve a shit-test response if one was pending
  6. turn-level hooks (frame, fractionation) — wired in P4
  7. aggregate -> apply_delta (clamp + normalize ladders) -> engagement drain
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Sequence

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence, Register
from roleplay_sim.domain.interfaces import Modifier, MoveRegistry
from roleplay_sim.domain.models import (
    Classification,
    GameFlags,
    GameState,
    ModContext,
    OutcomeResult,
    StateDelta,
    StateUpdate,
)
from roleplay_sim.config.tuning import TUNING
from roleplay_sim.engine import ladders
from roleplay_sim.engine.clamping import apply_delta, clamp

TurnHook = Callable[[Classification, GameState, PersonaConfig], OutcomeResult | None]

BASE_ENGAGEMENT_DRAIN = TUNING.base_engagement_drain


def _update_register_counters(flags: GameFlags, register: Register) -> None:
    if register == Register.PLOTLINE:
        flags.consecutive_plotline += 1
        flags.consecutive_baseline = 0
    elif register == Register.BASELINE:
        flags.consecutive_baseline += 1
        flags.consecutive_plotline = 0


def _delta_dict(d: StateDelta) -> dict[str, Any]:
    """Plain-dict view of a StateDelta for the (domain) event stream. Sparse."""
    out: dict[str, Any] = {}
    if d.emotional:
        out["emotional"] = {k: round(v, 3) for k, v in d.emotional.items()}
    if d.ladder_ceiling:
        out["ladder_ceiling"] = {lad.value: round(v, 3) for lad, v in d.ladder_ceiling.items()}
    if d.ladder_reached:
        out["ladder_reached"] = {lad.value: round(v, 3) for lad, v in d.ladder_reached.items()}
    if d.lock:
        out["lock"] = {lad.value: v for lad, v in d.lock.items()}
    if d.flags:
        out["flags"] = {k: (v.value if isinstance(v, Enum) else v) for k, v in d.flags.items()}
    return out


def _move_detail(move: Any) -> dict[str, Any]:
    """Readable summary of the classified move/action driving an outcome."""
    detail: dict[str, Any] = {}
    for attr in ("quality", "intensity", "target", "target_level", "intended_step", "softener"):
        if hasattr(move, attr):
            val = getattr(move, attr)
            detail[attr] = val.value if isinstance(val, Enum) else val
    lad = getattr(move, "ladder", None)
    if lad is not None:
        detail["ladder"] = lad.value if isinstance(lad, Enum) else lad
    return detail


def _resolve_test(outcome: str) -> tuple[StateDelta, list[Consequence]]:
    d = StateDelta()
    if outcome == "passed":
        d.emotional.update({"attraction": 12.0, "perceived_value": 10.0, "neediness": -3.0})
        return d, [Consequence.TEST_PASSED]
    if outcome == "failed":
        d.emotional.update({"attraction": -12.0, "perceived_value": -12.0, "neediness": 6.0})
        return d, [Consequence.TEST_FAILED]
    return d, []  # partial / ignored


@dataclass
class StateEngineImpl:
    registry: MoveRegistry
    modifiers: Sequence[Modifier] = ()
    turn_hooks: Sequence[TurnHook] = ()
    base_engagement_drain: float = BASE_ENGAGEMENT_DRAIN

    def apply(self, cls: Classification, state: GameState, persona: PersonaConfig) -> StateUpdate:
        new = deepcopy(state)
        events: list[dict[str, Any]] = []
        consequences: list[Consequence] = []
        agg = StateDelta()

        ceil_before = {lad.value: ls.ceiling for lad, ls in new.ladders.items()}
        ladders.passive_step(new, persona)
        passive = {
            k: {"from": round(ceil_before[k], 3), "to": round(new.ladders[lad].ceiling, 3)}
            for lad, k in ((lad, lad.value) for lad in new.ladders)
            if ceil_before[k] != new.ladders[lad].ceiling
        }
        if passive:
            events.append({"kind": "passive_accrual", "ceilings": passive})

        _update_register_counters(new.flags, cls.register)
        events.append({
            "kind": "register", "register": cls.register.value,
            "consecutive_baseline": new.flags.consecutive_baseline,
            "consecutive_plotline": new.flags.consecutive_plotline,
        })
        ctx = ModContext(frame=cls.frame, register=cls.register)

        def run(move: Any, kind: str) -> None:
            nonlocal agg
            res = self.registry.rule(move.type).resolve(move, new, persona)
            for mod in self.modifiers:
                res = mod.apply(move, res, new, persona, ctx)
            agg = agg.merged(res.delta)
            consequences.extend(res.consequences)
            events.append({
                "kind": kind,
                "move": move.type.value,
                "detail": _move_detail(move),
                "delta": _delta_dict(res.delta),
                "consequences": [c.value for c in res.consequences],
                "notes": res.notes,
            })
            new.flags.move_usage[move.type] = new.flags.move_usage.get(move.type, 0) + 1

        for mv in cls.moves:
            run(mv, "move")
        if cls.action is not None:
            run(cls.action, "action")

        if cls.shit_test_response is not None and new.flags.pending_test is not None:
            theme = new.flags.pending_test
            td, tcons = _resolve_test(cls.shit_test_response.outcome)
            agg = agg.merged(td)
            consequences.extend(tcons)
            events.append({
                "kind": "shit_test", "theme": theme,
                "outcome": cls.shit_test_response.outcome,
                "method": cls.shit_test_response.method,
                "delta": _delta_dict(td),
                "consequences": [c.value for c in tcons],
            })
            new.flags.pending_test = None

        for hook in self.turn_hooks:
            res = hook(cls, new, persona)
            if res is not None:
                agg = agg.merged(res.delta)
                consequences.extend(res.consequences)
                events.append({
                    "kind": "turn_hook",
                    "hook": getattr(hook, "__name__", "hook"),
                    "delta": _delta_dict(res.delta),
                    "consequences": [c.value for c in res.consequences],
                    "notes": res.notes,
                })

        apply_delta(new, agg)
        engagement_before_drain = new.emotional.engagement
        new.emotional.engagement = clamp(new.emotional.engagement - self.base_engagement_drain)
        events.append({
            "kind": "aggregate",
            "delta": _delta_dict(agg),
            "engagement_drain": self.base_engagement_drain,
            "engagement": {"before_drain": round(engagement_before_drain, 3),
                           "after_drain": round(new.emotional.engagement, 3)},
            "emotional_after": {k: round(v, 3) for k, v in asdict(new.emotional).items()},
        })
        return StateUpdate(new_state=new, consequences=consequences, events=events)
