from __future__ import annotations

from collections.abc import Sequence

from app.domain.models.recall import RecallCueType, RecallItemKind
from app.infrastructure.runtime.prompts.recall import (
    DRAFT_SYSTEM,
    HINT_SYSTEM,
    SCENARIOS_SYSTEM,
    RecallDraftOutput,
    RecallHintOutput,
    RecallScenariosOutput,
    build_draft_prompt,
    build_hint_prompt,
    build_scenarios_prompt,
    cue_ref,
)
from app.ports.integrations.llm_provider import LlmProvider
from app.ports.integrations.recall_drafter import CueContext, DraftedItem

# The current generator model (gpt-5.6-sol) only accepts the default
# temperature of 1, so faithfulness to the note comes from the prompt instead.
_DRAFT_TEMPERATURE = 1.0
_HINT_TEMPERATURE = 1.0
_SCENARIO_TEMPERATURE = 1.0


class LlmRecallDrafter:
    """LLM-backed `RecallDrafter` for the recall admin's AI capture.

    Cues are shown to the model under short refs (``c1``, ``c2``...) rather than
    UUIDs, and a returned ref is mapped back only if it names a cue that was
    passed in, so the model can never invent an id.
    """

    def __init__(self, llm: LlmProvider, *, model: str | None = None) -> None:
        self._llm = llm
        self._model = model

    async def draft_item(
        self, text: str, cues: Sequence[CueContext]
    ) -> DraftedItem:
        refs = {cue_ref(index): cue for index, cue in enumerate(cues)}
        prompt = build_draft_prompt(
            text,
            [
                (
                    ref,
                    cue.type.value,
                    cue.text,
                    [(line.hint, line.body) for line in cue.lines],
                )
                for ref, cue in refs.items()
            ],
        )
        result = await self._llm.complete_structured(
            messages=[
                {"role": "system", "content": DRAFT_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            response_model=RecallDraftOutput,
            temperature=_DRAFT_TEMPERATURE,
            model=self._model,
        )
        matched = refs.get((result.cue_ref or "").strip().lower())
        return DraftedItem(
            kind=RecallItemKind(result.kind),
            cue_id=matched.id if matched is not None else None,
            cue_text=result.cue_text,
            cue_type=RecallCueType(result.cue_type) if result.cue_type else None,
            hint=result.hint,
            sibling_hint=result.sibling_hint,
            title=result.title,
            body=result.body,
            delivery_note=result.delivery_note,
            question=result.question,
            steps=result.steps,
            scenarios=result.scenarios,
        )

    async def draft_scenarios(
        self,
        title: str,
        definition: str | None,
        existing: Sequence[str],
        count: int,
    ) -> list[str]:
        result = await self._llm.complete_structured(
            messages=[
                {"role": "system", "content": SCENARIOS_SYSTEM},
                {
                    "role": "user",
                    "content": build_scenarios_prompt(
                        title, definition, existing, count
                    ),
                },
            ],
            response_model=RecallScenariosOutput,
            temperature=_SCENARIO_TEMPERATURE,
            model=self._model,
        )
        return result.scenarios

    async def draft_hint(
        self,
        line: str,
        cue_text: str | None,
        avoid: Sequence[str],
    ) -> str:
        result = await self._llm.complete_structured(
            messages=[
                {"role": "system", "content": HINT_SYSTEM},
                {"role": "user", "content": build_hint_prompt(line, cue_text, avoid)},
            ],
            response_model=RecallHintOutput,
            temperature=_HINT_TEMPERATURE,
            model=self._model,
        )
        return result.hint
