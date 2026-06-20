"""Actor (LLM): renders her diegetic turn from the behavioral brief. [P6]

Non-streaming render() returns an ActorTurn (the API layer can stream separately
for TTS). Parses a trailing *[action]* out of the spoken line.
"""
from __future__ import annotations

import re
from typing import Any

from roleplay_sim.actor.prompt import build_messages
from roleplay_sim.domain.config import PersonaConfig, SceneConfig
from roleplay_sim.domain.interfaces import LLMClient
from roleplay_sim.domain.models import ActorTurn, BehavioralBrief

_ACTION = re.compile(r"\*\[([^\]]+)\]\*")


def split_action(text: str) -> tuple[str, str | None]:
    actions = _ACTION.findall(text or "")
    spoken = _ACTION.sub("", text or "").strip()
    return spoken, (actions[0].strip() if actions else None)


class LLMActor:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    async def render(self, brief: BehavioralBrief, persona: PersonaConfig,
                     scene: SceneConfig, history: Any) -> ActorTurn:
        messages = build_messages(brief, persona, scene, history)
        model = getattr(self.client, "model_for_act", lambda: None)()
        raw = await self.client.complete(messages, model=model, temperature=0.95, max_tokens=120)
        spoken, action = split_action(raw)
        return ActorTurn(text=spoken or "...", action=action)
