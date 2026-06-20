"""Escalation-ladder subsystem: permission ceiling, gap resolution, accrual. [P3]

This is the heart of *timing*. "Early vs. late" is not a clock — it is
`gap = target_level - ceiling`, where the ceiling rises with comfort/arousal,
accepted rungs, time-on-target, and blueprint, and drops/locks on over-reach.
Constants are inline for v1; they move to config/defaults.yaml in P8.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from roleplay_sim.config.tuning import TUNING
from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence, Ladder
from roleplay_sim.domain.models import GameState, StateDelta
from roleplay_sim.engine.clamping import clamp, clamp_level, normalize_ladder

# --- tunables (sourced from config/defaults.yaml via TUNING) ----------------
ACCRUAL_RATE = TUNING.accrual_rate
COMFORT_ACCRUAL = TUNING.comfort_accrual
AT_RISK_BAND = TUNING.at_risk_band
EIGHTY_BAND = TUNING.eighty_band
AT_RISK_COMFORT = TUNING.at_risk_comfort
LOCK_SEVERITY = TUNING.lock_severity


@dataclass
class EscalationOutcome:
    consequence: Consequence
    delta: StateDelta = field(default_factory=StateDelta)
    success: bool = False


def ceiling_target(state: GameState, ladder: Ladder, persona: PersonaConfig) -> float:
    """Where the ceiling *wants* to be given current emotional state + blueprint."""
    e = state.emotional
    if ladder == Ladder.PHYSICAL:
        base = 0.6 * e.comfort + 0.4 * e.arousal
    elif ladder == Ladder.VERBAL:
        base = 0.5 * e.comfort + 0.5 * e.attraction
    else:  # LOGISTICAL
        base = 0.7 * e.comfort + 0.3 * e.attraction
    growth = persona.blueprint.ladder_growth.get(ladder, 1.0)
    return clamp_level(base / 10.0 * growth)


def passive_step(state: GameState, persona: PersonaConfig) -> None:
    """Once per turn: comfort accrual + nudge each ceiling toward its target."""
    e = state.emotional
    if e.engagement > 25.0 and e.comfort > 8.0:
        e.comfort = clamp(e.comfort + COMFORT_ACCRUAL)
    for lad in Ladder:
        ls = state.ladders[lad]
        tgt = ceiling_target(state, lad, persona)
        ls.ceiling += ACCRUAL_RATE * (tgt - ls.ceiling)
        normalize_ladder(ls)


def _accepted(d: StateDelta, target: float, ladder: Ladder, eighty: bool) -> None:
    d.emotional["arousal"] = d.emotional.get("arousal", 0.0) + 4.0
    d.emotional["attraction"] = d.emotional.get("attraction", 0.0) + 2.0
    d.emotional["comfort"] = d.emotional.get("comfort", 0.0) + 1.0
    d.ladder_reached[ladder] = target
    # probe success raises the ceiling — faster when self-limiting in the 80% zone
    d.ladder_ceiling[ladder] = 1.2 if eighty else 0.6
    if eighty:
        d.emotional["comfort"] += 2.0
        d.emotional["attraction"] += 1.0


def resolve_escalation(
    state: GameState, ladder: Ladder, target_level: int, intended_step: int,
    persona: PersonaConfig,
) -> EscalationOutcome:
    """Resolve a physical/verbal/logistical escalation against the ladder."""
    ls = state.ladders[ladder]
    tl = float(target_level)
    d = StateDelta()

    # Hard-locked rung (point of no return).
    if ls.locked is not None and tl >= ls.locked:
        d.emotional.update({"comfort": -3.0, "engagement": -3.0})
        return EscalationOutcome(Consequence.LOCKED_OUT, d, False)

    # Deliberate step-back: builds comfort + tension, cheap re-escalation later.
    if intended_step < 0 or tl < ls.reached - 0.5:
        d.emotional["comfort"] = 2.0
        d.ladder_ceiling[ladder] = 0.3
        return EscalationOutcome(Consequence.RE_ESCALATION, d, True)

    # Re-escalation to an already-accepted level: safe.
    if tl <= ls.reached + 1e-6:
        d.emotional.update({"arousal": 2.0, "attraction": 1.0})
        return EscalationOutcome(Consequence.RE_ESCALATION, d, True)

    gap = tl - ls.ceiling
    if gap <= 0:
        _accepted(d, tl, ladder, eighty=(ls.ceiling - tl) <= EIGHTY_BAND)
        return EscalationOutcome(Consequence.ESCALATION_ACCEPTED, d, True)

    if gap <= AT_RISK_BAND:
        if state.emotional.comfort >= AT_RISK_COMFORT:
            _accepted(d, tl, ladder, eighty=False)
            return EscalationOutcome(Consequence.ESCALATION_ACCEPTED, d, True)
        d.emotional.update({"comfort": -2.0, "attraction": -1.0})
        return EscalationOutcome(Consequence.ESCALATION_RESISTED, d, False)

    # gap > 1 : premature over-reach.
    severity = min(gap, 3.0)
    d.emotional.update({
        "comfort": -3.0 - 2.0 * severity,
        "engagement": -3.0 - 2.0 * severity,
        "attraction": -2.0,
    })
    d.ladder_ceiling[ladder] = -1.0
    if gap > LOCK_SEVERITY or ladder == Ladder.LOGISTICAL:
        d.lock[ladder] = int(tl)
        return EscalationOutcome(Consequence.LOCKED_OUT, d, False)
    return EscalationOutcome(Consequence.ESCALATION_RESISTED, d, False)
