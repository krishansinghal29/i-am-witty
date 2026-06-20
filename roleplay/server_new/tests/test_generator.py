"""Meta-generator: roll determinism, the observable/latent firewall, offline +
LLM session assembly, and the per-turn voice spark. Plain asserts + asyncio.run
(no pytest), matching the rest of the suite.
"""
from __future__ import annotations

import asyncio
import random

from roleplay_sim.actor import prompt as actor_prompt
from roleplay_sim.actor.prompt import build_messages
from roleplay_sim.domain.config import PersonaConfig, SceneConfig
from roleplay_sim.domain.models import BehavioralBrief
from roleplay_sim.generator import rolls
from roleplay_sim.generator.session import generate_session, offline_session
from roleplay_sim.generator.synthesizer import first_impression_messages
from roleplay_sim.orchestrator.history import TurnHistoryImpl


# --- rolls ------------------------------------------------------------------
def test_roll_is_deterministic_under_seed():
    assert rolls.roll(seed=123) == rolls.roll(seed=123)


def test_different_seeds_differ():
    # Names alone won't always differ; compare the whole roll.
    assert rolls.roll(seed=1) != rolls.roll(seed=2)


def test_blueprint_in_expected_bands():
    for seed in range(25):
        bp = rolls.roll(seed=seed).persona.blueprint
        assert 0.2 <= bp.value_comfort_ratio <= 0.82
        assert 45.0 <= bp.close_threshold <= 68.0
        assert bp.escalation_style in {"leads", "passive", "guarded"}
        # anti-pattern moves are always penalized harder than comfort moves reward
        from roleplay_sim.domain.enums import MoveType
        assert bp.archetype_weights[MoveType.SUPPLICATE] > bp.archetype_weights[MoveType.RAPPORT]


# --- firewall ---------------------------------------------------------------
def test_first_impression_prompt_never_contains_latent():
    for seed in range(25):
        r = rolls.roll(seed=seed)
        blob = " ".join(m["content"] for m in
                         first_impression_messages(r.persona.observable, r.scene)).lower()
        lat = r.persona.latent
        for secret in [lat.name, str(lat.occupation), lat.hometown, *lat.hobbies]:
            assert secret.lower() not in blob, f"leaked {secret!r} (seed {seed})"


# --- session assembly -------------------------------------------------------
def test_offline_session_is_complete_and_no_llm():
    cfg = offline_session(seed=7)
    assert cfg.persona.identity["name"]
    assert cfg.persona.voice_palette                      # palette carried for the spark
    assert cfg.scene.first_impression.startswith("You spot her")
    assert cfg.scene.style and cfg.scene.age_hint         # observable appearance threaded
    assert cfg.persona.bible == ""                        # trait fallback path


class _SchemaFake:
    """Fake LLM that answers each structured call by schema (persona vs impression)."""

    async def complete_structured(self, messages, *, schema, model=None,
                                  temperature=0.2, max_tokens=800):
        if schema.__name__ == "PersonaSynth":
            return schema.model_validate({
                "bible": "You are Mara, 27.",
                "speaking_style": "dry and quick",
                "attracts": ["challenge"],
                "repels": ["neediness"],
                "mood_tonight": "a little bored",
                "fewshot": {"testing": ['She smirks. "Prove it."']},
            })
        return schema.model_validate({"text": "You spot her by the tall windows, coffee in hand."})

    async def complete(self, messages, *, model=None, temperature=0.7, max_tokens=400):
        return "..."

    async def stream(self, messages, *, model=None, temperature=0.9, max_tokens=300):
        yield "..."

    def model_for_author(self):
        return None

    def model_for_act(self):
        return None

    def model_for_classify(self):
        return None


def test_generate_session_uses_synth_output():
    cfg = asyncio.run(generate_session(_SchemaFake(), seed=3))
    assert cfg.persona.bible == "You are Mara, 27."
    assert cfg.persona.fewshot["testing"]
    assert cfg.scene.first_impression == "You spot her by the tall windows, coffee in hand."
    # blueprint/identity/palette still come from the (deterministic) roll
    assert cfg.persona.voice_palette == rolls.roll(seed=3).persona.voice_palette


def test_goal_can_be_pinned():
    assert offline_session(seed=5, goal="instant_date").scene.goal == "instant_date"


# --- per-turn spark ---------------------------------------------------------
def test_spark_offers_a_palette_word_when_enabled():
    persona = PersonaConfig(identity={"name": "X"}, voice_palette=["azure", "harbor"])
    saved = actor_prompt.SPARK_PROB
    actor_prompt.SPARK_PROB = 1.0
    try:
        msgs = build_messages(BehavioralBrief(), persona, SceneConfig(),
                              TurnHistoryImpl(), rng=random.Random(0))
    finally:
        actor_prompt.SPARK_PROB = saved
    user = msgs[1]["content"]
    assert "Loose inspiration" in user
    assert "azure" in user or "harbor" in user


def test_no_spark_when_disabled():
    persona = PersonaConfig(identity={"name": "X"}, voice_palette=["azure"])
    saved = actor_prompt.SPARK_PROB
    actor_prompt.SPARK_PROB = 0.0
    try:
        msgs = build_messages(BehavioralBrief(), persona, SceneConfig(),
                              TurnHistoryImpl(), rng=random.Random(0))
    finally:
        actor_prompt.SPARK_PROB = saved
    assert "Loose inspiration" not in msgs[1]["content"]
