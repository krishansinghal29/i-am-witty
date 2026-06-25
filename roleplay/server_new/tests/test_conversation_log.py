"""Conversation logging: capture-once / render-many, diffs, and Layer-C gating."""
from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

from roleplay_sim.domain.config import SessionConfig
from roleplay_sim.domain.models import GameState, PlayerTurn
from roleplay_sim.factory import build_llm_simulation
from roleplay_sim.llm.recording_client import LLMCallBuffer
from roleplay_sim.orchestrator.conversation_log import ConversationRecorder
from roleplay_sim.testing import (
    FakeLLMClient,
    build_stub_simulation,
    default_persona,
    default_scene,
)


def _recorder(out: Path, views, *, llm: bool = False) -> ConversationRecorder:
    return ConversationRecorder(
        out_dir=out, session_id="t", persona=default_persona(), scene=default_scene(),
        initial_state=GameState.fresh(), views=tuple(views),
        llm_buffer=LLMCallBuffer() if llm else None,
    )


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_stub_records_transcript_and_detailed_with_diff():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        rec = _recorder(out, ("transcript", "detailed"))
        sim = build_stub_simulation(recorder=rec)
        for _ in range(2):
            asyncio.run(sim.submit(PlayerTurn(text="hey")))

        transcript = _load(out / f"{rec.slug}.transcript.json")
        detailed = _load(out / f"{rec.slug}.detailed.json")

        # transcript: 2 turns -> 4 alternating messages
        assert [m["role"] for m in transcript["history"]] == \
            ["user", "assistant", "user", "assistant"]

        # detailed: chronological timeline, ordered player_input -> terminal
        assert len(detailed["turns"]) == 2
        stages = [e["stage"] for e in detailed["turns"][0]["events"]]
        assert stages[0] == "player_input" and stages[-1] == "terminal"
        assert "state_diff" in stages

        # the stub engine drains engagement by 1.0/turn; the diff must capture it
        diff = next(e for e in detailed["turns"][0]["events"] if e["stage"] == "state_diff")
        assert diff["emotional"]["engagement"]["delta"] == -1.0


def test_full_view_captures_llm_calls_by_stage():
    client = FakeLLMClient(
        structured={
            "register": "plotline",
            "moves": [{"type": "push_pull", "quality": "good"}],
            "frame": {"value_posture": "high", "congruence": True},
            "note": "intrigued but guarded",
            "recap": "he opened with a push-pull",
        },
        text="Hah, smooth. *[smirks]*",
    )
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        rec = _recorder(out, ("detailed", "full"), llm=True)
        cfg = SessionConfig(persona=default_persona(), scene=default_scene(),
                            initial_state=GameState.fresh())
        sim = build_llm_simulation(cfg, client, recorder=rec)
        asyncio.run(sim.submit(PlayerTurn(text="you look like trouble")))

        full = _load(out / f"{rec.slug}.full.json")
        turn = full["turns"][0]
        captured = {c["stage"] for c in turn["llm_calls"]}
        assert {"classify", "author", "act"} <= captured

        # raw calls are spliced onto their originating stage in the timeline
        by_stage = {e["stage"]: e for e in turn["events"]}
        assert by_stage["classification"]["llm"][0]["stage"] == "classify"
        assert by_stage["actor_render"]["llm"][0]["stage"] == "act"
        assert by_stage["actor_render"]["llm"][0]["response"]  # real prompt/response text


def _comfort_from_sources(events: list[dict]) -> float:
    """Sum every per-source comfort contribution in a turn's timeline."""
    total = 0.0
    for e in events:
        if e["stage"] == "engine.passive_accrual" and "comfort" in e:
            total += e["comfort"]["delta"]
        elif e["stage"] in ("engine.move", "engine.turn_hook", "engine.shit_test"):
            total += e.get("delta", {}).get("emotional", {}).get("comfort", 0.0)
    return total


def test_passive_comfort_is_logged_and_reconciles():
    # Real engine path so passive_step (comfort + ceilings) actually runs.
    client = FakeLLMClient(
        structured={
            "register": "plotline",
            "moves": [{"type": "push_pull", "quality": "good", "target": "personality"}],
            "frame": {"value_posture": "high", "congruence": True},
            "note": "x", "recap": "y",
        },
        text="Hah. *[smirks]*",
    )
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        rec = _recorder(out, ("detailed",))
        cfg = SessionConfig(persona=default_persona(), scene=default_scene(),
                            initial_state=GameState.fresh())
        sim = build_llm_simulation(cfg, client, recorder=rec)
        asyncio.run(sim.submit(PlayerTurn(text="you look like trouble")))

        events = _load(out / f"{rec.slug}.detailed.json")["turns"][0]["events"]
        passive = next(e for e in events if e["stage"] == "engine.passive_accrual")
        assert "comfort" in passive   # the previously-dropped passive comfort bump

        diff = next(e for e in events if e["stage"] == "state_diff")
        net = diff["emotional"]["comfort"]["delta"]
        # per-source deltas must reconcile to the net diff (the point of the log)
        assert round(_comfort_from_sources(events), 6) == round(net, 6)


def test_full_view_skipped_without_llm_capture():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        rec = _recorder(out, ("full",), llm=False)   # 'full' listed but no buffer
        sim = build_stub_simulation(recorder=rec)
        asyncio.run(sim.submit(PlayerTurn(text="hey")))
        assert not (out / f"{rec.slug}.full.json").exists()
