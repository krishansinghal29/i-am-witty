"""Actor (LLM): renders her diegetic turn from the behavioral brief. [P6]

render() returns an ActorTurn holding ONE combined string — spoken words in
double quotes interleaved with short third-person narration. The API streams it
verbatim (display + TTS read the whole thing); there is no spoken/action split.
"""
from __future__ import annotations

from typing import Any

from roleplay_sim.actor.prompt import build_messages
from roleplay_sim.domain.config import PersonaConfig, SceneConfig
from roleplay_sim.domain.interfaces import LLMClient
from roleplay_sim.llm.tracing import llm_stage
from roleplay_sim.domain.models import ActorTurn, BehavioralBrief


class LLMActor:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    async def render(self, brief: BehavioralBrief, persona: PersonaConfig,
                     scene: SceneConfig, history: Any) -> ActorTurn:
        messages = build_messages(brief, persona, scene, history)
        model = getattr(self.client, "model_for_act", lambda: None)()
        with llm_stage("act"):
            raw = await self.client.complete(messages, model=model, temperature=0.95, max_tokens=160)
        return ActorTurn(text=(raw or "").strip() or "...")
