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
from dataclasses import dataclass, field
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

        ladders.passive_step(new, persona)
        _update_register_counters(new.flags, cls.register)
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
                "consequences": [c.value for c in res.consequences],
                "notes": res.notes,
            })
            new.flags.move_usage[move.type] = new.flags.move_usage.get(move.type, 0) + 1

        for mv in cls.moves:
            run(mv, "move")
        if cls.action is not None:
            run(cls.action, "action")

        if cls.shit_test_response is not None and new.flags.pending_test is not None:
            td, tcons = _resolve_test(cls.shit_test_response.outcome)
            agg = agg.merged(td)
            consequences.extend(tcons)
            events.append({"kind": "shit_test", "outcome": cls.shit_test_response.outcome})
            new.flags.pending_test = None

        for hook in self.turn_hooks:
            res = hook(cls, new, persona)
            if res is not None:
                agg = agg.merged(res.delta)
                consequences.extend(res.consequences)
                if res.notes:
                    events.append({"kind": "turn_hook", "notes": res.notes})

        apply_delta(new, agg)
        new.emotional.engagement = clamp(new.emotional.engagement - self.base_engagement_drain)
        return StateUpdate(new_state=new, consequences=consequences, events=events)
