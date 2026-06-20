"""MoveRegistry: MoveType/ActionType -> MoveMeta (ladder, default level, OutcomeRule). [P3/P3b]

`build_registry()` wires every move/action to its rule. Action ladder metadata is
encoded here since the ladder subsystem needs it.
"""
from __future__ import annotations

from typing import Any

from roleplay_sim.domain.config import MoveMeta
from roleplay_sim.domain.enums import ActionType, Ladder, MoveType
from roleplay_sim.domain.models import GameState, OutcomeResult, StateDelta
from roleplay_sim.engine.rules import (
    anti_patterns,
    attraction,
    close,
    comfort,
    evaluate,
    frame_tools,
    narrative,
    openers,
    premise,
)
from roleplay_sim.engine.rules.actions import EscalationActionRule


class DefaultRule:
    """Neutral fallback for move types without a registered rule."""

    def resolve(self, move: Any, state: GameState, persona: Any) -> OutcomeResult:
        return OutcomeResult(delta=StateDelta(), consequences=[], notes="default(noop)")


# ActionType -> (Ladder, default rung 0-10)
ACTION_LADDER: dict[ActionType, tuple[Ladder, int]] = {
    ActionType.STOP_HER: (Ladder.PHYSICAL, 0),
    ActionType.PLANT_FEET: (Ladder.PHYSICAL, 0),
    ActionType.STEP_BACK: (Ladder.PHYSICAL, 0),
    ActionType.SIT_DOWN: (Ladder.PHYSICAL, 1),
    ActionType.TAP_SHOULDER: (Ladder.PHYSICAL, 1),
    ActionType.HOLD_GAZE: (Ladder.PHYSICAL, 1),
    ActionType.TOUCH_LIGHT: (Ladder.PHYSICAL, 2),
    ActionType.TOUCH_ESCALATE: (Ladder.PHYSICAL, 4),
    ActionType.LEAN_IN: (Ladder.PHYSICAL, 4),
    ActionType.KISS_ATTEMPT: (Ladder.PHYSICAL, 5),
    ActionType.SUGGEST_ISOLATE: (Ladder.LOGISTICAL, 3),
    ActionType.SUGGEST_VENUE_CHANGE: (Ladder.LOGISTICAL, 5),
    ActionType.PULL: (Ladder.LOGISTICAL, 7),
}

# Verbal moves that ride the verbal escalation ladder (their rules call it).
VERBAL_LADDER: dict[MoveType, tuple[Ladder, int]] = {
    MoveType.MISINTERPRET: (Ladder.VERBAL, 4),
    MoveType.SEXUALIZE: (Ladder.VERBAL, 6),
}

# MoveType -> rule instance.
_MOVE_RULES: dict[MoveType, Any] = {
    # openers
    MoveType.OPEN_DIRECT: openers.DirectOpenRule(),
    MoveType.OPEN_INDIRECT: openers.IndirectOpenRule(),
    MoveType.OPEN_PUSH_PULL: openers.PushPullOpenRule(),
    MoveType.OPEN_SITUATIONAL: openers.SituationalOpenRule(),
    MoveType.OPEN_OBSERVATIONAL: openers.ObservationalOpenRule(),
    MoveType.OPEN_NONVERBAL: openers.NonverbalOpenRule(),
    MoveType.OPEN_OPINION: openers.OpinionOpenRule(),
    # attraction
    MoveType.TEASE: attraction.TeaseRule(),
    MoveType.PUSH_PULL: attraction.PushPullRule(),
    MoveType.COLD_READ: attraction.ColdReadRule(),
    MoveType.DISQUALIFY: attraction.DisqualifyRule(),
    MoveType.COCKY_FRAME: attraction.CockyFrameRule(),
    MoveType.OPEN_LOOP: attraction.OpenLoopRule(),
    MoveType.EXAGGERATION: attraction.ExaggerationRule(),
    MoveType.MISINTERPRET: attraction.MisinterpretRule(),
    MoveType.SEXUALIZE: attraction.SexualizeRule(),
    # premise
    MoveType.PREMISE_SUBTLE: premise.PremiseSubtleRule(),
    MoveType.PREMISE_OVERT: premise.PremiseOvertRule(),
    # evaluate
    MoveType.QUALIFY_ASK: evaluate.QualifyAskRule(),
    MoveType.QUALIFY_TEASE: evaluate.QualifyTeaseRule(),
    MoveType.QUALIFY_LEAD: evaluate.QualifyLeadRule(),
    MoveType.QUALIFY_HAVE_VALUE: evaluate.QualifyHaveValueRule(),
    # narrative
    MoveType.STORY_SHOW: narrative.StoryShowRule(),
    MoveType.STORY_TELL: narrative.StoryTellRule(),
    MoveType.SELF_DISCLOSURE: narrative.SelfDisclosureRule(),
    MoveType.PREFRAME: narrative.PreframeRule(),
    MoveType.REFRAME: narrative.ReframeRule(),
    MoveType.SOCIAL_PROOF: narrative.SocialProofRule(),
    # comfort
    MoveType.GENUINE_QUESTION: comfort.GenuineQuestionRule(),
    MoveType.ACTIVE_LISTENING: comfort.ActiveListeningRule(),
    MoveType.RAPPORT: comfort.RapportRule(),
    MoveType.AGREE_EXAGGERATE: comfort.AgreeExaggerateRule(),
    # frame tools
    MoveType.SOCIAL_PRESSURE: frame_tools.SocialPressureRule(),
    MoveType.SEEDING: frame_tools.SeedingRule(),
    MoveType.BABYSTEP: frame_tools.BabystepRule(),
    MoveType.FALSE_TIME_CONSTRAINT: frame_tools.FalseTimeConstraintRule(),
    MoveType.ASSUME_BURDEN: frame_tools.AssumeBurdenRule(),
    # close
    MoveType.CLOSE_NUMBER: close.CloseNumberRule(),
    MoveType.CLOSE_DATE: close.CloseDateRule(),
    MoveType.CLOSE_INSTANT_DATE: close.CloseInstantDateRule(),
    # anti-patterns
    MoveType.SUPPLICATE: anti_patterns.SupplicateRule(),
    MoveType.INTERVIEW_QS: anti_patterns.InterviewQsRule(),
    MoveType.TRY_HARD: anti_patterns.TryHardRule(),
    MoveType.OVER_EXPLAIN: anti_patterns.OverExplainRule(),
    MoveType.SEEK_VALIDATION: anti_patterns.SeekValidationRule(),
}


class MoveRegistryImpl:
    def __init__(self) -> None:
        self._meta: dict[Any, MoveMeta] = {}
        self._default = DefaultRule()

    def register(self, mt: Any, *, ladder=None, default_level=None, rule=None) -> None:
        self._meta[mt] = MoveMeta(ladder=ladder, default_level=default_level,
                                  rule=rule or self._default)

    def meta(self, move_type: Any) -> MoveMeta:
        return self._meta.get(move_type, MoveMeta())

    def rule(self, move_type: Any):
        m = self._meta.get(move_type)
        return m.rule if (m and m.rule) else self._default


def build_registry() -> MoveRegistryImpl:
    reg = MoveRegistryImpl()
    action_rule = EscalationActionRule()
    for at, (lad, lvl) in ACTION_LADDER.items():
        reg.register(at, ladder=lad, default_level=lvl, rule=action_rule)
    for mt, rule in _MOVE_RULES.items():
        lad, lvl = VERBAL_LADDER.get(mt, (None, None))
        reg.register(mt, ladder=lad, default_level=lvl, rule=rule)
    return reg
