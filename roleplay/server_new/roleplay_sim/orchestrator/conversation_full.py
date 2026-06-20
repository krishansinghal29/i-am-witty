"""The `full` view: detailed timeline + raw LLM prompts/responses. [Layer C view]

Kept in its own module so Layer C is fully detachable: nothing in the
transcript/detailed path imports this, and the recorder only imports it lazily
when the 'full' view is enabled (which itself requires LLM capture to be on).

Implemented by composition over `conversation_log.turn_block` (include_llm=True),
not inheritance — it reuses the single timeline builder and only opts into the
LLM splicing that builder already supports.
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from roleplay_sim.orchestrator.conversation_log import header, turn_block

if TYPE_CHECKING:
    from roleplay_sim.orchestrator.conversation_log import ConversationRecorder


def render_full(rec: "ConversationRecorder") -> dict[str, Any]:
    return {**header(rec), "turns": [turn_block(t, include_llm=True) for t in rec.turns]}
