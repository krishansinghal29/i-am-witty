"""Conversation logging: capture once, render to several files. [logging core]

`ConversationRecorder` is the single capture point. `Simulation` hands it raw
domain objects per turn (it does no derivation itself); the recorder owns the
typed `TurnRecord`, the before/after state diff, and the projection to disk.

Each enabled *view* is a plain render function (no Protocol/registry) producing
one JSON file per session, rewritten every turn — mirroring the old server's
best-effort dump:

    transcript : persona/scene header + flat history (parity with the old log)
    detailed   : chronological per-turn event timeline + state diffs (Layers A+B)
    full       : detailed + raw LLM prompts/responses (Layer C) — lives in
                 conversation_full.py and is imported lazily only when enabled.
"""
from __future__ import annotations

import dataclasses
import json
import logging
import os
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from roleplay_sim.domain.config import PersonaConfig, SceneConfig
from roleplay_sim.domain.models import (
    ActionMove,
    ActorTurn,
    BehavioralBrief,
    Classification,
    DirectorStep,
    GameState,
    Move,
    PlayerTurn,
)
from roleplay_sim.domain.enums import Consequence, SessionStatus
from roleplay_sim.llm.recording_client import LLMCall, LLMCallBuffer

logger = logging.getLogger("roleplay.conversation_log")

# server_new/tmp/conversations  (parents: orchestrator -> roleplay_sim -> server_new)
DEFAULT_LOG_DIR = Path(__file__).resolve().parents[2] / "tmp" / "conversations"


# ---------------------------------------------------------------------------
# Typed record (the real contract every view reads)
# ---------------------------------------------------------------------------
@dataclass
class TurnRecord:
    """One fully-captured turn. Holds live domain objects (typed), not dicts;
    serialization is a render concern handled below."""
    turn_index: int
    player: PlayerTurn
    classification: Classification
    state_before: GameState
    state_after: GameState
    consequences: list[Consequence]
    engine_events: list[dict[str, Any]]     # domain event stream from StateEngine
    pending_test: Optional[str]
    brief: BehavioralBrief
    actor: ActorTurn
    status: SessionStatus
    llm_calls: list[LLMCall] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Serialization helpers (domain -> JSON-able primitives)
# ---------------------------------------------------------------------------
def _e(v: Any) -> Any:
    """Render an enum to its value; pass primitives through."""
    return v.value if isinstance(v, Enum) else v


def _json_default(o: Any) -> Any:
    if isinstance(o, Enum):
        return o.value
    if dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)
    if isinstance(o, set):
        return sorted(_e(x) for x in o)
    return str(o)


def serialize_state(s: GameState) -> dict[str, Any]:
    return {
        "emotional": dataclasses.asdict(s.emotional),
        "ladders": {
            _e(lad): {"ceiling": ls.ceiling, "reached": ls.reached, "locked": ls.locked}
            for lad, ls in s.ladders.items()
        },
        "flags": _serialize_flags(s),
    }


def _serialize_flags(s: GameState) -> dict[str, Any]:
    f = s.flags
    return {
        "premise_set": f.premise_set,
        "qualified": f.qualified,
        "narrative_seeded": f.narrative_seeded,
        "venue": f.venue,
        "turn_count": f.turn_count,
        "consecutive_baseline": f.consecutive_baseline,
        "consecutive_plotline": f.consecutive_plotline,
        "supplication_count": f.supplication_count,
        "move_usage": {_e(k): v for k, v in f.move_usage.items()},
        "pending_test": f.pending_test,
    }


def _serialize_move(m: Move) -> dict[str, Any]:
    return {
        "type": _e(m.type), "quality": _e(m.quality), "intensity": _e(m.intensity),
        "softener": m.softener, "target": m.target,
        "ladder": _e(m.ladder), "target_level": m.target_level,
    }


def _serialize_action(a: Optional[ActionMove]) -> Optional[dict[str, Any]]:
    if a is None:
        return None
    return {"type": _e(a.type), "ladder": _e(a.ladder),
            "target_level": a.target_level, "intended_step": a.intended_step}


def serialize_classification(c: Classification) -> dict[str, Any]:
    return {
        "register": _e(c.register),
        "moves": [_serialize_move(m) for m in c.moves],
        "frame": {
            "value_posture": _e(c.frame.value_posture),
            "supplication": _e(c.frame.supplication),
            "reaction_seeking": c.frame.reaction_seeking,
            "congruence": c.frame.congruence,
        },
        "action": _serialize_action(c.action),
        "shit_test_response": (
            {"outcome": c.shit_test_response.outcome, "method": c.shit_test_response.method}
            if c.shit_test_response else None
        ),
    }


def serialize_brief(b: BehavioralBrief) -> dict[str, Any]:
    return {
        "beat": _e(b.beat),
        "secondary_beat": _e(b.secondary_beat),
        "dials": {
            "warmth": _e(b.dials.warmth), "investment": _e(b.dials.investment),
            "testiness": _e(b.dials.testiness), "openness": _e(b.dials.openness),
            "receptiveness": _e(b.dials.receptiveness),
        },
        "note": b.note, "recap": b.recap,
    }


def serialize_persona(p: PersonaConfig) -> dict[str, Any]:
    """Readable persona summary; omits the large static bible/fewshot text."""
    bp = p.blueprint
    return {
        "identity": p.identity,
        "archetype": p.archetype,
        "speaking_style": p.speaking_style,
        "attracts": list(p.attracts),
        "repels": list(p.repels),
        "mood_tonight": p.mood_tonight,
        "blueprint": {
            "value_comfort_ratio": bp.value_comfort_ratio,
            "close_threshold": bp.close_threshold,
            "escalation_style": bp.escalation_style,
        },
    }


def serialize_llm_call(call: LLMCall) -> dict[str, Any]:
    return {
        "stage": call.stage, "kind": call.kind, "model": call.model,
        "latency_ms": round(call.latency_ms, 1),
        "temperature": call.temperature, "max_tokens": call.max_tokens,
        "messages": call.messages, "response": call.response,
    }


# ---------------------------------------------------------------------------
# State diff (owned by the recorder, not the orchestrator)
# ---------------------------------------------------------------------------
def diff_state(before: GameState, after: GameState) -> dict[str, Any]:
    """Structured before->after delta; only changed entries are included."""
    out: dict[str, Any] = {}

    emo: dict[str, Any] = {}
    for k, b in dataclasses.asdict(before.emotional).items():
        a = getattr(after.emotional, k)
        if abs(a - b) > 1e-9:
            emo[k] = {"from": round(b, 3), "to": round(a, 3), "delta": round(a - b, 3)}
    if emo:
        out["emotional"] = emo

    lad: dict[str, Any] = {}
    for key, bl in before.ladders.items():
        al = after.ladders.get(key)
        if al is None:
            continue
        changes: dict[str, Any] = {}
        for fld in ("ceiling", "reached", "locked"):
            bv, av = getattr(bl, fld), getattr(al, fld)
            if bv != av:
                changes[fld] = {"from": bv, "to": av}
        if changes:
            lad[_e(key)] = changes
    if lad:
        out["ladders"] = lad

    flags: dict[str, Any] = {}
    bf, af = _serialize_flags(before), _serialize_flags(after)
    for k in af:
        if bf.get(k) != af.get(k):
            flags[k] = {"from": bf.get(k), "to": af.get(k)}
    if flags:
        out["flags"] = flags

    return out


# ---------------------------------------------------------------------------
# Timeline builder (shared by detailed + full; composition, not inheritance)
# ---------------------------------------------------------------------------
# Which timeline stage each LLM stage tag attaches to (used by the full view).
LLM_STAGE_TO_EVENT = {"classify": "classification", "author": "brief_author", "act": "actor_render"}


def build_timeline(
    turn: TurnRecord, llm_by_stage: Optional[dict[str, list[dict[str, Any]]]] = None,
) -> list[dict[str, Any]]:
    """Ordered chronological events for one turn. If `llm_by_stage` is given, the
    raw LLM calls are spliced onto their originating stage (full view only)."""
    events: list[dict[str, Any]] = []

    def emit(stage: str, body: dict[str, Any]) -> None:
        ev = {"stage": stage, **body}
        if llm_by_stage:
            llm_stage = next((k for k, v in LLM_STAGE_TO_EVENT.items() if v == stage), None)
            if llm_stage and llm_by_stage.get(llm_stage):
                ev["llm"] = llm_by_stage[llm_stage]
        events.append(ev)

    emit("player_input",
         {"text": turn.player.text, "action": _serialize_action(turn.player.action)})
    emit("classification", serialize_classification(turn.classification))

    # Engine's domain event stream -> "engine.<kind>" timeline entries.
    for ev in turn.engine_events:
        body = {k: v for k, v in ev.items() if k != "kind"}
        emit(f"engine.{ev.get('kind', 'event')}", body)

    emit("consequences", {"items": [_e(c) for c in turn.consequences]})
    emit("test_trigger", {"pending_test": turn.pending_test})
    emit("beat_policy", {
        "beat": _e(turn.brief.beat),
        "secondary_beat": _e(turn.brief.secondary_beat),
        "dials": serialize_brief(turn.brief)["dials"],
    })
    emit("brief_author", {"note": turn.brief.note, "recap": turn.brief.recap})
    emit("actor_render", {"text": turn.actor.text, "action": turn.actor.action})
    emit("state_diff", diff_state(turn.state_before, turn.state_after))
    emit("terminal", {"status": _e(turn.status)})
    return events


def turn_block(turn: TurnRecord, include_llm: bool = False) -> dict[str, Any]:
    llm_by_stage: Optional[dict[str, list[dict[str, Any]]]] = None
    if include_llm:
        llm_by_stage = {}
        for call in turn.llm_calls:
            llm_by_stage.setdefault(call.stage, []).append(serialize_llm_call(call))
    block = {
        "turn": turn.turn_index,
        "status_after": _e(turn.status),
        "events": build_timeline(turn, llm_by_stage),
        "state_after": serialize_state(turn.state_after),
    }
    if include_llm:
        block["llm_calls"] = [serialize_llm_call(c) for c in turn.llm_calls]
    return block


# ---------------------------------------------------------------------------
# Views (plain render functions)
# ---------------------------------------------------------------------------
def header(rec: "ConversationRecorder") -> dict[str, Any]:
    return {
        "slug": rec.slug,
        "session_id": rec.session_id,
        "created": rec.created,
        "updated": _utc_stamp(),
        "persona": serialize_persona(rec.persona),
        "scene": dataclasses.asdict(rec.scene),
        "initial_state": serialize_state(rec.initial_state),
    }


def render_transcript(rec: "ConversationRecorder") -> dict[str, Any]:
    """Flat persona + history view (parity with the old server log)."""
    history: list[dict[str, str]] = []
    for t in rec.turns:
        user = t.player.text
        if t.player.action is not None:
            user = f"{user}  *[{_e(t.player.action.type)}]*".strip()
        history.append({"role": "user", "content": user})
        assistant = t.actor.text
        if t.actor.action:
            assistant = f"{assistant} *[{t.actor.action}]*"
        history.append({"role": "assistant", "content": assistant})
    return {**header(rec), "history": history}


def render_detailed(rec: "ConversationRecorder") -> dict[str, Any]:
    """Chronological per-turn timeline + state diffs (Layers A+B, no raw LLM)."""
    return {**header(rec), "turns": [turn_block(t, include_llm=False) for t in rec.turns]}


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%f")


def _renderer(view: str) -> Optional[Callable[["ConversationRecorder"], dict[str, Any]]]:
    if view == "transcript":
        return render_transcript
    if view == "detailed":
        return render_detailed
    if view == "full":
        # Layer C lives in its own module; import only when actually requested.
        from roleplay_sim.orchestrator.conversation_full import render_full
        return render_full
    return None


# ---------------------------------------------------------------------------
# Recorder (single capture point)
# ---------------------------------------------------------------------------
@dataclass
class ConversationRecorder:
    out_dir: Path
    session_id: str
    persona: PersonaConfig
    scene: SceneConfig
    initial_state: GameState
    views: tuple[str, ...] = ("transcript", "detailed")
    llm_buffer: Optional[LLMCallBuffer] = None
    slug: str = ""
    created: str = ""
    turns: list[TurnRecord] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.created = _utc_stamp()
        name = (self.persona.identity or {}).get("name", "fixed")
        self.slug = f"{self.created}_{name}"

    def record_turn(
        self, player: PlayerTurn, state_before: GameState,
        cls: Classification, step: DirectorStep, actor: ActorTurn, status: SessionStatus,
    ) -> None:
        """Capture one turn from raw domain objects. Best-effort: never raises."""
        try:
            turn = TurnRecord(
                turn_index=len(self.turns) + 1,
                player=player,
                classification=cls,
                state_before=state_before,        # Simulation hands a fresh pre-update copy
                # Freeze after-state now: some engines return the live state object,
                # which would keep mutating on later turns if held by reference.
                state_after=deepcopy(step.state),
                consequences=list(step.consequences),
                engine_events=list(step.events),
                pending_test=step.state.flags.pending_test,
                brief=step.brief,
                actor=actor,
                status=status,
                llm_calls=self.llm_buffer.drain() if self.llm_buffer else [],
            )
            self.turns.append(turn)
            self._dump()
        except Exception:
            logger.exception("conversation record_turn failed")

    def _dump(self) -> None:
        try:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            for view in self.views:
                if view == "full" and self.llm_buffer is None:
                    continue  # nothing to render without Layer C capture
                render = _renderer(view)
                if render is None:
                    continue
                doc = render(self)
                path = self.out_dir / f"{self.slug}.{view}.json"
                path.write_text(
                    json.dumps(doc, ensure_ascii=False, indent=2, default=_json_default),
                    encoding="utf-8",
                )
        except Exception:
            logger.exception("conversation dump failed")


def _truthy(v: str | None) -> bool:
    return (v or "").lower() in {"1", "true", "yes", "on"}


def build_recorder_from_env(
    session_id: str, persona: PersonaConfig, scene: SceneConfig, initial_state: GameState,
) -> Optional[ConversationRecorder]:
    """Build a recorder from env, or None if logging is disabled.

    ROLEPLAY_LOG_CONVERSATIONS  master switch (truthy)
    ROLEPLAY_LOG_DIR            output dir (default server_new/tmp/conversations)
    ROLEPLAY_LOG_VIEWS          comma list (default 'transcript,detailed'; '+full' if LLM on)
    ROLEPLAY_LOG_LLM            capture raw prompts/responses for the 'full' view (truthy)
    """
    if not _truthy(os.environ.get("ROLEPLAY_LOG_CONVERSATIONS")):
        return None
    out_dir = Path(os.environ.get("ROLEPLAY_LOG_DIR") or DEFAULT_LOG_DIR)
    llm_on = _truthy(os.environ.get("ROLEPLAY_LOG_LLM"))
    raw_views = os.environ.get("ROLEPLAY_LOG_VIEWS")
    if raw_views:
        views = tuple(v.strip() for v in raw_views.split(",") if v.strip())
    else:
        views = ("transcript", "detailed", "full") if llm_on else ("transcript", "detailed")
    return ConversationRecorder(
        out_dir=out_dir, session_id=session_id, persona=persona, scene=scene,
        initial_state=deepcopy(initial_state), views=views,
        llm_buffer=LLMCallBuffer() if llm_on else None,
    )
