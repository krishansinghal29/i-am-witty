"""Load an authored persona directory into a PersonaConfig. [P7]

A persona is a folder with persona.yaml + bible.md + fewshot.yaml. Unknown
move/ladder keys in the blueprint are skipped rather than raising.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from roleplay_sim.domain.config import Blueprint, PersonaConfig
from roleplay_sim.domain.enums import Ladder, MoveType

_DIR = Path(__file__).resolve().parent


def _move_weights(raw: dict | None) -> dict[MoveType, float]:
    out: dict[MoveType, float] = {}
    for k, v in (raw or {}).items():
        try:
            out[MoveType(k)] = float(v)
        except (ValueError, TypeError):
            continue
    return out


def _ladder_growth(raw: dict | None) -> dict[Ladder, float]:
    out: dict[Ladder, float] = {}
    for k, v in (raw or {}).items():
        try:
            out[Ladder(k)] = float(v)
        except (ValueError, TypeError):
            continue
    return out


def load_persona(name: str) -> PersonaConfig:
    folder = _DIR / name
    data = yaml.safe_load((folder / "persona.yaml").read_text(encoding="utf-8")) or {}
    bible = (folder / "bible.md").read_text(encoding="utf-8")
    fewshot = yaml.safe_load((folder / "fewshot.yaml").read_text(encoding="utf-8")) or {}

    bp = data.get("blueprint", {}) or {}
    blueprint = Blueprint(
        value_comfort_ratio=float(bp.get("value_comfort_ratio", 0.5)),
        close_threshold=float(bp.get("close_threshold", 55.0)),
        escalation_style=str(bp.get("escalation_style", "passive")),
        archetype_weights=_move_weights(bp.get("archetype_weights")),
        ladder_growth=_ladder_growth(bp.get("ladder_growth")),
    )
    return PersonaConfig(
        identity=data.get("identity", {}),
        archetype=data.get("archetype", name),
        blueprint=blueprint,
        speaking_style=data.get("speaking_style", ""),
        attracts=list(data.get("attracts", [])),
        repels=list(data.get("repels", [])),
        mood_tonight=data.get("mood_tonight", ""),
        bible=bible,
        fewshot={k: list(v) for k, v in fewshot.items()},
    )
