"""Stub assembly for the walking skeleton and tests. [P2]

Provides trivial implementations of the deterministic + LLM-facing sub-components
so the full turn loop runs with no LLM and no real engine yet. Real components
replace these in P3–P6 via `build_simulation` factories later.
"""
from __future__ import annotations

from roleplay_sim.actor.stub_actor import StubActor
from roleplay_sim.classifier.stub_classifier import StubClassifier
from roleplay_sim.director.director import DirectorImpl
from roleplay_sim.domain.config import (
    Blueprint,
    PersonaConfig,
    SceneConfig,
    SessionConfig,
)
from roleplay_sim.domain.enums import Beat, Consequence
from roleplay_sim.domain.models import (
    Classification,
    Dials,
    GameState,
    StateUpdate,
)
from roleplay_sim.orchestrator.simulation import Simulation
from roleplay_sim.orchestrator.terminal import TerminalCheckerImpl


class StubStateEngine:
    """No-op engine: passes state through, nudges engagement so the loop moves."""
    registry = None
    modifiers: list = []

    def apply(self, cls: Classification, state: GameState, persona: PersonaConfig) -> StateUpdate:
        state.emotional.engagement = max(0.0, state.emotional.engagement - 1.0)
        return StateUpdate(new_state=state, consequences=[], events=[])


class StubBeatPolicy:
    def select(self, state: GameState, consequences, persona):
        if Consequence.TEST_TRIGGERED in consequences:
            return Beat.SHIT_TEST, None, Dials()
        return Beat.NEUTRAL_ENGAGE, None, Dials()


class StubTestTrigger:
    def maybe_test(self, state: GameState, persona: PersonaConfig):
        return None


class StubBriefAuthor:
    async def author(self, state, beat, dials, consequences, history, persona):
        return f"(stub note: beat={beat.value})", "(stub recap)"


def default_persona() -> PersonaConfig:
    return PersonaConfig(
        identity={"name": "Sofia", "age": 26, "occupation": "designer"},
        archetype="princess",
        blueprint=Blueprint(value_comfort_ratio=0.7, close_threshold=55.0),
        speaking_style="short, slightly teasing",
        attracts=["challenge", "confidence"],
        repels=["neediness", "try-hard"],
        mood_tonight="mildly bored",
    )


def default_scene() -> SceneConfig:
    return SceneConfig(venue="rooftop bar", approach_context="cold approach", goal="number")


def build_stub_simulation(cfg: SessionConfig | None = None, *, recorder=None) -> Simulation:
    cfg = cfg or SessionConfig(
        persona=default_persona(),
        scene=default_scene(),
        initial_state=GameState.fresh(),
    )
    director = DirectorImpl(
        state_engine=StubStateEngine(),
        beat_policy=StubBeatPolicy(),
        brief_author=StubBriefAuthor(),
        test_trigger=StubTestTrigger(),
    )
    return Simulation(
        cfg=cfg,
        classifier=StubClassifier(),
        director=director,
        actor=StubActor(),
        terminal=TerminalCheckerImpl(),
        recorder=recorder,
    )


class FakeLLMClient:
    """In-memory LLMClient for tests: no litellm, no keys, no network."""

    def __init__(self, *, structured: dict | None = None, text: str = "...") -> None:
        self._structured = structured or {}
        self._text = text

    async def complete(self, messages, *, model=None, temperature=0.7, max_tokens=400) -> str:
        return self._text

    async def complete_structured(self, messages, *, schema, model=None,
                                  temperature=0.2, max_tokens=800):
        return schema.model_validate(self._structured)

    async def stream(self, messages, *, model=None, temperature=0.9, max_tokens=300):
        for tok in self._text.split(" "):
            yield tok + " "

    def model_for_classify(self):  # noqa: D401
        return None

    def model_for_author(self):
        return None

    def model_for_act(self):
        return None
