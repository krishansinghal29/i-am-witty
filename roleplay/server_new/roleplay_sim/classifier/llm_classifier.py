"""LLM Classifier: PlayerTurn -> Classification via structured output. [P6]

Robust, forgiving parsing: unknown move/action strings are dropped rather than
raising, so a sloppy model response degrades gracefully.
"""
from __future__ import annotations

from typing import Any

from roleplay_sim.classifier.prompt import SCHEMA, build_messages, context_summary
from roleplay_sim.domain.enums import (
    ActionType,
    LMH,
    MoveType,
    Quality,
    Register,
    Supplication,
    ValuePosture,
)
from roleplay_sim.domain.interfaces import LLMClient
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


def _enum(enum_cls, val, default):
    try:
        return enum_cls(val)
    except Exception:
        return default


def _parse_move(d: dict[str, Any]) -> Move | None:
    mt = _enum(MoveType, d.get("type"), None)
    if mt is None:
        return None
    lad, _lvl = VERBAL_LADDER.get(mt, (None, None))
    return Move(
        type=mt,
        quality=_enum(Quality, d.get("quality"), Quality.MEDIOCRE),
        intensity=_enum(LMH, d.get("intensity"), LMH.MED),
        softener=bool(d.get("softener", False)),
        target=str(d.get("target", "none")),
        ladder=lad,
        target_level=d.get("target_level"),
    )


def _parse_action(d: dict[str, Any] | None) -> ActionMove | None:
    if not d:
        return None
    at = _enum(ActionType, d.get("type"), None)
    if at is None:
        return None
    lad, default_level = ACTION_LADDER.get(at, (None, 1))
    if lad is None:
        return None
    level = d.get("target_level")
    return ActionMove(
        type=at,
        ladder=lad,
        target_level=int(level) if isinstance(level, int) else default_level,
        intended_step=int(d.get("intended_step") or 1),
    )


def parse_classification(data: dict[str, Any]) -> Classification:
    fr = data.get("frame") or {}
    frame = Frame(
        value_posture=_enum(ValuePosture, fr.get("value_posture"), ValuePosture.NEUTRAL),
        supplication=_enum(Supplication, fr.get("supplication"), Supplication.NONE),
        reaction_seeking=bool(fr.get("reaction_seeking", False)),
        congruence=bool(fr.get("congruence", True)),
    )
    moves = [m for m in (_parse_move(x) for x in (data.get("moves") or [])) if m]
    st = data.get("shit_test_response")
    str_resp = (
        ShitTestResponse(outcome=st.get("outcome", "partial"), method=st.get("method", "unreactive"))
        if isinstance(st, dict) and st.get("outcome")
        else None
    )
    return Classification(
        register=_enum(Register, data.get("register"), Register.BASELINE),
        moves=moves,
        frame=frame,
        action=_parse_action(data.get("action")),
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
        data = await self.client.complete_structured(messages, schema=SCHEMA, model=model)
        cls = parse_classification(data)
        if turn.action is not None and cls.action is None:
            cls.action = turn.action  # trust an explicitly-supplied action
        return cls
