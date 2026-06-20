"""Classifier prompt + JSON schema (co-located with the classifier). [P6]

The classifier tags the MAN's turn against the verbal-game taxonomy. It does NOT
judge timing or the woman's state — only what he did. Timing/gates are derived
downstream from the ladder + outcome rules.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from roleplay_sim.domain.enums import (
    ActionType,
    LMH,
    MoveType,
    Quality,
    Register,
    Supplication,
    ValuePosture,
)
from roleplay_sim.domain.models import GameState

_MOVES = ", ".join(m.value for m in MoveType)
_ACTIONS = ", ".join(a.value for a in ActionType)


# ---------------------------------------------------------------------------
# Structured-output schema (bare — field meaning lives in SYSTEM, refined later)
# ---------------------------------------------------------------------------
class MoveOut(BaseModel):
    type: MoveType
    quality: Quality = Quality.MEDIOCRE
    intensity: LMH = LMH.MED
    softener: bool = False
    target: str = "none"
    target_level: Optional[int] = None


class FrameOut(BaseModel):
    value_posture: ValuePosture = ValuePosture.NEUTRAL
    supplication: Supplication = Supplication.NONE
    reaction_seeking: bool = False
    congruence: bool = True


class ActionOut(BaseModel):
    type: ActionType
    target_level: Optional[int] = None
    intended_step: Optional[int] = None


class ShitTestOut(BaseModel):
    outcome: Literal["passed", "partial", "failed"]
    method: str = "unreactive"


class ClassificationOut(BaseModel):
    # `register` collides with BaseModel's inherited ABCMeta.register, so the
    # Python attribute is renamed while the wire/schema key stays "register".
    model_config = ConfigDict(populate_by_name=True)

    speech_register: Register = Field(default=Register.BASELINE, alias="register")
    moves: list[MoveOut] = Field(default_factory=list)
    frame: FrameOut = Field(default_factory=FrameOut)
    action: Optional[ActionOut] = None
    shit_test_response: Optional[ShitTestOut] = None


SYSTEM = f"""You label a man's single conversational turn while he flirts with a woman, \
using a fixed taxonomy. Output JSON only.

register: baseline (normal talk) | plotline (emotionally charged spike) | mixed.

move types: {_MOVES}

action types (non-verbal/logistical, optional): {_ACTIONS}

For each move give: type, quality (good/mediocre/botched), intensity (low/med/high), \
softener (bool), target, and target_level (0-10) only for escalation moves.

frame (always): value_posture (high/neutral/low), supplication (none/mild/strong), \
reaction_seeking (bool), congruence (bool — does the turn fit naturally).

If the previous turn from her was a shit test, set shit_test_response with how he handled it.
Only tag what is actually present. Do not invent moves."""


def context_summary(state: GameState, history: Any) -> str:
    f = state.flags
    bits = [
        f"premise_set={f.premise_set}",
        f"pending_test={f.pending_test!r}",
        f"venue={f.venue}",
        f"turn={f.turn_count}",
    ]
    last_her = ""
    try:
        win = history.window(2)
        if win:
            last_her = win[-1][1].text
    except Exception:
        pass
    if last_her:
        bits.append(f'her_last="{last_her}"')
    return "; ".join(bits)


def build_messages(turn_text: str, action_hint: str, ctx: str) -> list[dict[str, str]]:
    user = f"Context: {ctx}\n"
    if action_hint:
        user += f"Player physical/logistical action: {action_hint}\n"
    user += f'Player said: "{turn_text}"\n\nReturn the JSON label.'
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
