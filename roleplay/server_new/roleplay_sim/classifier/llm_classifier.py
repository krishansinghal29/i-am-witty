"""LLM Classifier: PlayerTurn -> Classification via structured output. [P6]

The model returns a validated `ClassificationOut` (pydantic); `parse_classification`
maps it to the domain `Classification`, enriching moves/actions with their ladder
from the registry (the model never sees ladders). A response that violates the
schema raises at validation time rather than being silently coerced.
"""
from __future__ import annotations

from typing import Any

from roleplay_sim.classifier.prompt import (
    ActionOut,
    ClassificationOut,
    MoveOut,
    build_messages,
    context_summary,
)
from roleplay_sim.domain.interfaces import LLMClient
from roleplay_sim.llm.tracing import llm_stage
from roleplay_sim.domain.models import (
    ActionMove,
    Classification,
    Frame,
    GameState,
    Move,
    PlayerTurn,
    ShitTestResponse,
)
from roleplay_sim.engine.registry import ACTION_LADDER, VERBAL_LADDER


def _to_move(m: MoveOut) -> Move:
    lad, _lvl = VERBAL_LADDER.get(m.type, (None, None))
    return Move(
        type=m.type,
        quality=m.quality,
        intensity=m.intensity,
        softener=m.softener,
        target=m.target,
        ladder=lad,
        target_level=m.target_level,
    )


def _to_action(a: ActionOut | None) -> ActionMove | None:
    if a is None:
        return None
    lad, default_level = ACTION_LADDER[a.type]   # every ActionType has ladder meta
    return ActionMove(
        type=a.type,
        ladder=lad,
        target_level=a.target_level if a.target_level is not None else default_level,
        intended_step=a.intended_step if a.intended_step is not None else 1,
    )


def parse_classification(out: ClassificationOut) -> Classification:
    frame = Frame(
        value_posture=out.frame.value_posture,
        supplication=out.frame.supplication,
        reaction_seeking=out.frame.reaction_seeking,
        congruence=out.frame.congruence,
    )
    st = out.shit_test_response
    str_resp = ShitTestResponse(outcome=st.outcome, method=st.method) if st else None
    return Classification(
        register=out.speech_register,
        moves=[_to_move(m) for m in out.moves],
        frame=frame,
        action=_to_action(out.action),
        shit_test_response=str_resp,
    )


class LLMClassifier:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    async def classify(self, turn: PlayerTurn, state: GameState, history: Any) -> Classification:
        ctx = context_summary(state, history)
        action_hint = turn.action.type.value if turn.action else ""
        messages = build_messages(turn.text, action_hint, ctx)
        model = getattr(self.client, "model_for_classify", lambda: None)()
        with llm_stage("classify"):
            out = await self.client.complete_structured(messages, schema=ClassificationOut, model=model)
        cls = parse_classification(out)
        if turn.action is not None and cls.action is None:
            cls.action = turn.action  # trust an explicitly-supplied action
        return cls
