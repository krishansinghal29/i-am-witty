"""Assemble a rolled session into the engine's SessionConfig.

Two entry points:
- `generate_session` (async, LLM): roll -> synthesize persona + first impression.
- `offline_session` (sync, no LLM): roll -> trait-derived persona + fallback
  first impression. Used by the CLI and deterministic tests (no keys, no network).

The rolled blueprint, identity, scene, and voice palette are identical on both
paths; only the prose (bible / few-shot / first impression) differs.
"""
from __future__ import annotations

import asyncio

from roleplay_sim.domain.config import PersonaConfig, SceneConfig, SessionConfig
from roleplay_sim.domain.interfaces import LLMClient
from roleplay_sim.domain.models import GameState
from roleplay_sim.generator import rolls
from roleplay_sim.generator.rolls import Rolled
from roleplay_sim.generator.synthesizer import (
    PersonaSynth,
    fallback_first_impression,
    synthesize_first_impression,
    synthesize_persona,
)


def _identity(r: Rolled) -> dict:
    lat = r.persona.latent
    return {
        "name": lat.name,
        "age": lat.age,
        "occupation": lat.occupation,
        "hometown": lat.hometown,
        "hobbies": list(lat.hobbies),
    }


def _scene_config(r: Rolled, first_impression: str) -> SceneConfig:
    s, obs = r.scene, r.persona.observable
    return SceneConfig(
        venue=s.venue,
        approach_context=s.approach_context,
        present_company=s.present_company,
        time_of_day=s.time_of_day,
        goal=s.goal,
        difficulty=s.difficulty,
        first_impression=first_impression,
        style=obs.style,
        body_shape=obs.body_shape,
        age_hint=obs.age_hint,
    )


def _persona_config(r: Rolled, synth: PersonaSynth | None) -> PersonaConfig:
    p = r.persona
    if synth is not None:
        bible, style = synth.bible, synth.speaking_style
        attracts, repels = synth.attracts, synth.repels
        mood, fewshot = synth.mood_tonight, synth.fewshot
    else:
        # Trait-only fallback: empty bible makes the Actor's character_system build
        # a system prompt from these fields directly.
        bible, fewshot = "", {}
        style = f"{p.axes.warmth}, {p.axes.testiness}-testiness; {p.axes.motivation}-oriented"
        attracts = [p.axes.motivation, "a man who holds his frame", "being made to chase a little"]
        repels = ["neediness", "trying too hard", "seeking her approval"]
        mood = f"{p.axes.warmth}, not expecting much tonight"
    return PersonaConfig(
        identity=_identity(r),
        archetype=p.archetype,
        blueprint=p.blueprint,
        speaking_style=style,
        attracts=attracts,
        repels=repels,
        mood_tonight=mood,
        bible=bible,
        fewshot=fewshot,
        voice_palette=list(p.voice_palette),
    )


def _session(r: Rolled, synth: PersonaSynth | None, first_impression: str) -> SessionConfig:
    return SessionConfig(
        persona=_persona_config(r, synth),
        scene=_scene_config(r, first_impression),
        initial_state=GameState.fresh(),
    )


async def generate_session(client: LLMClient, *, seed: int | None = None,
                           goal: str | None = None) -> SessionConfig:
    """Roll a woman + scene, then synthesize her persona and opening snapshot."""
    r = rolls.roll(seed, goal=goal)
    synth, first_impression = await asyncio.gather(
        synthesize_persona(client, r.persona, r.scene),
        synthesize_first_impression(client, r.persona.observable, r.scene),
    )
    return _session(r, synth, first_impression)


def offline_session(*, seed: int | None = None, goal: str | None = None) -> SessionConfig:
    """No-LLM session for the CLI and tests: trait-derived persona + fallback snapshot."""
    r = rolls.roll(seed, goal=goal)
    fi = fallback_first_impression(r.persona.observable, r.scene)
    return _session(r, None, fi)
