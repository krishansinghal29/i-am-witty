"""Deterministic stub Actor for the walking skeleton + tests. [P2]

Renders a canned line keyed to the beat so the loop is observable without an LLM.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig, SceneConfig
from roleplay_sim.domain.enums import Beat
from roleplay_sim.domain.models import ActorTurn, BehavioralBrief

_LINES: dict[Beat, tuple[str, str | None]] = {
    Beat.LEAVE: ("Yeah, I'm gonna head back to my friends.", "walks off"),
    Beat.COOL_OFF: ("Mm. Okay.", "glances away"),
    Beat.POLITE_BRUSHOFF: ("That's nice. Anyway—", None),
    Beat.NEUTRAL_ENGAGE: ("Oh? Go on.", None),
    Beat.CURIOUS: ("Wait, what do you mean?", None),
    Beat.SHIT_TEST: ("Bold of you. Did I say you could sit?", None),
    Beat.QUALIFY_SELF: ("I mean, I do a lot more than just this.", None),
    Beat.WARM_OPEN: ("Haha okay, you're kind of funny.", "smiles"),
    Beat.BANTER: ("Wow, big talk for a stranger.", None),
    Beat.COMPLY: ("Okay, sure, lead the way.", None),
    Beat.ESCALATE_BACK: ("...you're trouble, you know that?", "leans in"),
    Beat.BRAKES: ("Hey—slow down a sec.", "pulls back"),
    Beat.FLAKE_SIGNAL: ("Maybe. We'll see.", None),
}


class StubActor:
    async def render(
        self, brief: BehavioralBrief, persona: PersonaConfig, scene: SceneConfig,
        history: object,
    ) -> ActorTurn:
        text, action = _LINES.get(brief.beat, ("...", None))
        return ActorTurn(text=text, action=action)
