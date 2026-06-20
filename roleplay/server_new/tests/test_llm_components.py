"""LLM-backed component tests using the in-memory FakeLLMClient (no litellm/keys). [P6]"""
from __future__ import annotations

import asyncio

import pydantic

from roleplay_sim.actor.actor import LLMActor, split_action
from roleplay_sim.classifier.llm_classifier import LLMClassifier, parse_classification
from roleplay_sim.classifier.prompt import ClassificationOut
from roleplay_sim.director.brief_author import LLMBriefAuthor
from roleplay_sim.domain.enums import (
    ActionType,
    Beat,
    Ladder,
    MoveType,
    Register,
    SessionStatus,
    ValuePosture,
)
from roleplay_sim.domain.models import BehavioralBrief, GameState, PlayerTurn
from roleplay_sim.factory import build_llm_simulation
from roleplay_sim.orchestrator.history import TurnHistoryImpl
from roleplay_sim.testing import FakeLLMClient, default_persona, default_scene
from roleplay_sim.domain.config import SessionConfig


def test_parse_classification_maps_to_domain_with_ladders():
    out = ClassificationOut.model_validate({
        "register": "plotline",
        "moves": [
            {"type": "misinterpret", "quality": "good", "intensity": "med"},
            {"type": "tease"},
        ],
        "frame": {"value_posture": "high", "supplication": "none", "congruence": True},
        "action": {"type": "sit_down"},
    })
    cls = parse_classification(out)
    assert cls.register is Register.PLOTLINE
    assert [m.type for m in cls.moves] == [MoveType.MISINTERPRET, MoveType.TEASE]
    assert cls.moves[0].ladder is Ladder.VERBAL   # enriched from the registry
    assert cls.moves[1].ladder is None            # tease doesn't ride a ladder
    assert cls.frame.value_posture is ValuePosture.HIGH
    assert cls.action.type is ActionType.SIT_DOWN
    assert cls.action.ladder is not None and cls.action.target_level is not None


def test_invalid_enum_now_raises():
    # graceful degradation is gone: an unknown move type fails validation
    try:
        ClassificationOut.model_validate({"moves": [{"type": "not_a_real_move"}]})
        raise AssertionError("expected a ValidationError")
    except pydantic.ValidationError:
        pass


def test_split_action():
    spoken, action = split_action("Bold of you. *[glances away]*")
    assert spoken == "Bold of you."
    assert action == "glances away"


def test_classifier_uses_client():
    client = FakeLLMClient(structured={
        "register": "plotline",
        "moves": [{"type": "tease", "quality": "good"}],
        "frame": {"value_posture": "high"},
    })
    cls = asyncio.run(
        LLMClassifier(client).classify(PlayerTurn(text="you're trouble"), GameState.fresh(), TurnHistoryImpl())
    )
    assert cls.moves[0].type is MoveType.TEASE


def test_brief_author_returns_note_and_recap():
    client = FakeLLMClient(structured={"note": "stay aloof", "recap": "he just sat down"})
    note, recap = asyncio.run(
        LLMBriefAuthor(client).author(
            GameState.fresh(), Beat.SHIT_TEST,
            BehavioralBrief().dials, [], TurnHistoryImpl(), default_persona(),
        )
    )
    assert note == "stay aloof"
    assert recap == "he just sat down"


def test_actor_renders_text_and_action():
    client = FakeLLMClient(text="Did I say you could sit? *[raises eyebrow]*")
    turn = asyncio.run(
        LLMActor(client).render(BehavioralBrief(), default_persona(), default_scene(), TurnHistoryImpl())
    )
    assert "sit" in turn.text
    assert turn.action == "raises eyebrow"


def test_full_llm_simulation_round_trip():
    # one combined structured payload satisfies both the classifier and the brief author
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
    cfg = SessionConfig(persona=default_persona(), scene=default_scene(), initial_state=GameState.fresh())
    sim = build_llm_simulation(cfg, client)
    actor_turn, status = asyncio.run(sim.submit(PlayerTurn(text="you look like trouble")))
    assert actor_turn.text
    assert status is SessionStatus.ONGOING
    assert sim.state.emotional.attraction > 8.0   # the push-pull raised attraction
    assert sim.state.flags.move_usage.get(MoveType.PUSH_PULL) == 1
