"""TestTrigger: when she initiates a shit test. [P5]

Explicit (deterministic) trigger so testing is reliable enough to practice
against: she tests once she reads him as emotionally relevant (perceived_value
crosses a threshold) but hasn't won her yet (attraction not high), on a cadence
so it doesn't fire every turn. Value-driven blueprints test more readily.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.models import GameState

_THEMES = [
    "he's being overly familiar",
    "is he actually interesting or just confident",
    "testing whether he'll supplicate",
    "checking if he can hold his frame",
]


class TestTriggerImpl:
    def maybe_test(self, state: GameState, persona: PersonaConfig) -> str | None:
        if state.flags.pending_test:
            return None
        e = state.emotional
        threshold = 50.0 - 10.0 * persona.blueprint.value_comfort_ratio
        relevant = e.perceived_value >= threshold and e.attraction < 55.0
        cadence = state.flags.turn_count % 2 == 0  # not every turn
        if relevant and cadence:
            return _THEMES[state.flags.turn_count % len(_THEMES)]
        return None
