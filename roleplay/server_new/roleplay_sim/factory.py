"""Assembly factories. [P4 -> extended P5/P6]

Central place to wire concrete components together. Grows as later phases add the
director glue and the real LLM-backed components.
"""
from __future__ import annotations

from roleplay_sim.actor.actor import LLMActor
from roleplay_sim.classifier.llm_classifier import LLMClassifier
from roleplay_sim.director.beat_policy import BeatPolicyImpl
from roleplay_sim.director.brief_author import LLMBriefAuthor
from roleplay_sim.director.director import DirectorImpl
from roleplay_sim.director.test_trigger import TestTriggerImpl
from roleplay_sim.domain.config import SessionConfig
from roleplay_sim.domain.interfaces import Actor, BriefAuthor, Classifier, LLMClient
from roleplay_sim.engine.modifiers import default_modifiers, default_turn_hooks
from roleplay_sim.engine.registry import build_registry
from roleplay_sim.engine.state_engine import StateEngineImpl
from roleplay_sim.orchestrator.simulation import Simulation
from roleplay_sim.orchestrator.terminal import TerminalCheckerImpl


def build_state_engine() -> StateEngineImpl:
    """The full deterministic engine: registry + per-move modifiers + turn hooks."""
    return StateEngineImpl(
        registry=build_registry(),
        modifiers=default_modifiers(),
        turn_hooks=default_turn_hooks(),
    )


def build_director(brief_author: BriefAuthor) -> DirectorImpl:
    """Real director: deterministic engine + beat policy + test trigger; the
    brief author is the only LLM-backed sub-component (stubbed before P6)."""
    return DirectorImpl(
        state_engine=build_state_engine(),
        beat_policy=BeatPolicyImpl(),
        brief_author=brief_author,
        test_trigger=TestTriggerImpl(),
    )


def build_simulation(
    cfg: SessionConfig, *, classifier: Classifier, actor: Actor, brief_author: BriefAuthor,
) -> Simulation:
    return Simulation(
        cfg=cfg,
        classifier=classifier,
        director=build_director(brief_author),
        actor=actor,
        terminal=TerminalCheckerImpl(),
    )


def build_llm_simulation(cfg: SessionConfig, client: LLMClient) -> Simulation:
    """Full simulation with the three LLM-backed components sharing one client."""
    return build_simulation(
        cfg,
        classifier=LLMClassifier(client),
        actor=LLMActor(client),
        brief_author=LLMBriefAuthor(client),
    )
