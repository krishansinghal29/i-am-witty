"""BeatPolicy: deterministic map from state bands + consequences -> Beat + Dials. [P5]

Consequences (what just happened) take precedence; otherwise we fall back to the
emotional bands. Dials are derived from state so the Actor performs the right
warmth/investment/testiness without ever seeing the raw numbers.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Beat, Consequence, Ladder, LMH
from roleplay_sim.domain.models import Dials, GameState

LEAVE_ENGAGEMENT = 8.0


def to_lmh(v: float, lo: float = 30.0, hi: float = 60.0) -> LMH:
    return LMH.LOW if v < lo else (LMH.MED if v < hi else LMH.HIGH)


def _dials(state: GameState) -> Dials:
    e = state.emotional
    ceiling = max(state.ladders[Ladder.PHYSICAL].ceiling,
                  state.ladders[Ladder.VERBAL].ceiling)
    return Dials(
        warmth=to_lmh(e.comfort),
        investment=to_lmh((e.attraction + e.engagement) / 2.0),
        testiness=to_lmh(e.perceived_value - e.attraction + 20.0, 30.0, 55.0),
        openness=to_lmh(e.comfort),
        receptiveness=to_lmh(ceiling * 10.0),
    )


class BeatPolicyImpl:
    def select(self, state: GameState, consequences: list[Consequence],
               persona: PersonaConfig) -> tuple[Beat, "Beat | None", Dials]:
        e = state.emotional
        dials = _dials(state)
        cons = set(consequences)

        def out(beat: Beat, secondary: "Beat | None" = None):
            return beat, secondary, dials

        # 1) hard signals
        if e.engagement <= LEAVE_ENGAGEMENT:
            return out(Beat.LEAVE)
        if Consequence.CLOSE_ACCEPTED in cons:
            return out(Beat.COMPLY)
        if Consequence.CLOSE_FLAKY in cons:
            return out(Beat.FLAKE_SIGNAL)
        if Consequence.CLOSE_REJECTED in cons:
            return out(Beat.COOL_OFF)
        if Consequence.LOCKED_OUT in cons:
            return out(Beat.BRAKES, Beat.COOL_OFF)

        # 2) her pending/just-resolved test
        if state.flags.pending_test:
            return out(Beat.SHIT_TEST)
        if Consequence.TEST_PASSED in cons:
            return out(Beat.WARM_OPEN, Beat.BANTER)
        if Consequence.TEST_FAILED in cons:
            return out(Beat.COOL_OFF)

        # 3) move-driven reactions
        if Consequence.SHE_QUALIFIES in cons:
            return out(Beat.QUALIFY_SELF)
        if Consequence.FEELS_INTERVIEWED in cons:
            return out(Beat.POLITE_BRUSHOFF)
        if Consequence.ESCALATION_ACCEPTED in cons:
            return out(Beat.ESCALATE_BACK if e.arousal > 40 else Beat.COMPLY)
        if Consequence.ESCALATION_RESISTED in cons:
            return out(Beat.BRAKES)
        if Consequence.BORED in cons:
            return out(Beat.POLITE_BRUSHOFF)

        # 4) fall back to emotional bands
        if e.neediness > 45:
            return out(Beat.COOL_OFF)
        if e.attraction >= 55 and e.comfort >= 45:
            return out(Beat.WARM_OPEN, Beat.BANTER)
        if e.attraction >= 30:
            return out(Beat.BANTER if e.comfort >= 30 else Beat.CURIOUS)
        if e.attraction >= 15:
            return out(Beat.CURIOUS)
        return out(Beat.NEUTRAL_ENGAGE)
