"""Classifier prompt + JSON schema (co-located with the classifier). [P6]

The classifier tags the MAN's turn against the verbal-game taxonomy. It does NOT
judge timing or the woman's state — only what he did. Timing/gates are derived
downstream from the ladder + outcome rules.
"""
from __future__ import annotations

from typing import Any

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

SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "register": {"type": "string", "enum": [r.value for r in Register]},
        "moves": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "quality": {"type": "string", "enum": [q.value for q in Quality]},
                    "intensity": {"type": "string", "enum": [i.value for i in LMH]},
                    "softener": {"type": "boolean"},
                    "target": {"type": "string"},
                    "target_level": {"type": ["integer", "null"]},
                },
                "required": ["type"],
            },
        },
        "frame": {
            "type": "object",
            "properties": {
                "value_posture": {"type": "string", "enum": [v.value for v in ValuePosture]},
                "supplication": {"type": "string", "enum": [s.value for s in Supplication]},
                "reaction_seeking": {"type": "boolean"},
                "congruence": {"type": "boolean"},
            },
        },
        "action": {
            "type": ["object", "null"],
            "properties": {
                "type": {"type": "string"},
                "target_level": {"type": ["integer", "null"]},
                "intended_step": {"type": ["integer", "null"]},
            },
        },
        "shit_test_response": {
            "type": ["object", "null"],
            "properties": {
                "outcome": {"type": "string", "enum": ["passed", "partial", "failed"]},
                "method": {"type": "string"},
            },
        },
    },
    "required": ["register", "moves", "frame"],
}

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
