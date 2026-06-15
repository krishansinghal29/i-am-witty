from __future__ import annotations

import logging
import random

from app.infrastructure.runtime.prompts.character_generator import generate_character
from app.infrastructure.runtime.prompts.roleplay.registry import get_roleplay_spec
from app.infrastructure.runtime.prompts.roleplay.spec import RoleplayContext, RoleplaySpec
from app.infrastructure.runtime.prompts.word_lists import word_list
from app.ports.integrations.llm_provider import LlmProvider
from app.ports.integrations.tts_provider import TtsProvider
from app.ports.task_runtime_engine import (
    CompleteTaskRuntimeInput,
    GeneratedPrompt,
    GeneratedTaskPayload,
    GenerateTaskInput,
    PromptMessage,
    RolePlayOpening,
    TaskRuntimeResult,
    TurnResult,
    TurnTaskRuntimeInput,
)

logger = logging.getLogger(__name__)

# Roleplay favours variety in both the character and the line generation.
_GENERATION_TEMPERATURE = 1.0
_DEFAULT_VERB_COUNT = 10


class RoleplayTaskEngine:
    """LLM-backed `TaskRuntimeEngine` for multi-turn ``roleplay_v1`` tasks.

    Unlike the single-shot voice engine, this engine is conversational: ``generate``
    produces the opening (character + first line), and each ``turn`` runs ONE
    combined LLM call that simultaneously grades the user's last line, reacts in
    character, and writes her next line — advancing the persisted conversation
    state until the misinterpretation goal is reached. ``complete`` is unused
    (completion is driven by the goal-reaching turn).
    """

    def __init__(
        self,
        llm: LlmProvider,
        tts: TtsProvider | None = None,
        *,
        generator_model: str | None = None,
        tts_voice: str | None = None,
    ) -> None:
        self._llm = llm
        self._tts = tts
        self._generator_model = generator_model
        self._tts_voice = tts_voice

    async def generate(self, input: GenerateTaskInput) -> GeneratedTaskPayload:
        spec = get_roleplay_spec(self._backend_key(input.task))
        verbs = self._sample_verbs(input.task)
        target = self._target_count(input.task, spec)

        character = await generate_character(self._llm, model=self._generator_model)

        ctx = RoleplayContext(
            persona=character.persona,
            appearance=character.appearance,
            verbs=verbs,
            verb_cursor=0,
            landed_count=0,
            target_count=target,
            conversation=[],
        )
        opening = await self._llm.complete_structured(
            messages=[
                {"role": "system", "content": spec.build_system(ctx)},
                {"role": "user", "content": spec.build_opening_user(ctx)},
            ],
            response_model=spec.opening_schema,
            temperature=_GENERATION_TEMPERATURE,
            model=self._generator_model,
        )

        conversation = [
            {"role": "she_narration", "content": opening.narration},
            {"role": "she", "content": opening.dialogue},
        ]
        runtime_state = {
            "roleplay": {
                "backend_key": spec.key,
                "character": {
                    "persona": character.persona,
                    "appearance": character.appearance,
                },
                "verbs": verbs,
                "verb_cursor": self._next_cursor(0, verbs),
                "landed_count": 0,
                "target_count": target,
                "safety_max_turns": spec.safety_max_turns,
                "turn_count": 0,
                "brief_heading": opening.brief_heading,
                "conversation": conversation,
            }
        }

        audio_base64, audio_content_type = await self._synthesize(
            opening.dialogue, input
        )

        return GeneratedTaskPayload(
            prompt=GeneratedPrompt(
                messages=(PromptMessage(role="She", content=opening.dialogue),),
                speech_text=opening.dialogue,
            ),
            audio_base64=audio_base64,
            audio_content_type=audio_content_type,
            roleplay=RolePlayOpening(
                brief_heading=opening.brief_heading,
                narration=opening.narration,
                dialogue=opening.dialogue,
                target_count=target,
                landed_count=0,
                appearance=character.appearance,
                runtime_state=runtime_state,
            ),
        )

    async def complete(self, input: CompleteTaskRuntimeInput) -> TaskRuntimeResult:
        raise NotImplementedError("roleplay tasks complete via turn(), not complete()")

    async def turn(self, input: TurnTaskRuntimeInput) -> TurnResult:
        rp = (input.runtime_state or {}).get("roleplay") or {}
        spec = get_roleplay_spec(rp.get("backend_key") or self._backend_key(input.task))

        verbs = list(rp.get("verbs") or [])
        verb_cursor = int(rp.get("verb_cursor", 0))
        landed_count = int(rp.get("landed_count", 0))
        target = int(rp.get("target_count") or spec.target_count)
        turn_count = int(rp.get("turn_count", 0))
        safety_max_turns = int(rp.get("safety_max_turns", spec.safety_max_turns))
        character = rp.get("character") or {}

        conversation = list(rp.get("conversation") or [])
        conversation.append({"role": "you", "content": input.user_transcript})

        ctx = RoleplayContext(
            persona=character.get("persona", ""),
            appearance=character.get("appearance", ""),
            verbs=verbs,
            verb_cursor=min(verb_cursor, max(len(verbs) - 1, 0)),
            landed_count=landed_count,
            target_count=target,
            conversation=conversation,
        )
        turn = await self._llm.complete_structured(
            messages=[
                {"role": "system", "content": spec.build_system(ctx)},
                {"role": "user", "content": spec.build_turn_user(ctx)},
            ],
            response_model=spec.turn_schema,
            temperature=_GENERATION_TEMPERATURE,
            model=self._generator_model,
        )

        new_landed = landed_count + (1 if turn.landed else 0)
        new_turn_count = turn_count + 1
        goal_reached = new_landed >= target
        capped = new_turn_count >= safety_max_turns
        is_complete = bool(turn.is_complete or goal_reached or capped)

        conversation.append({"role": "she_narration", "content": turn.narration})
        conversation.append({"role": "she", "content": turn.dialogue})

        new_runtime_state = {
            "roleplay": {
                **rp,
                "conversation": conversation,
                "verb_cursor": self._next_cursor(verb_cursor, verbs),
                "landed_count": new_landed,
                "turn_count": new_turn_count,
                "target_count": target,
            }
        }

        audio_base64, audio_content_type = await self._synthesize_text(turn.dialogue)

        return TurnResult(
            narration=turn.narration,
            dialogue=turn.dialogue,
            landed=turn.landed,
            intensity=turn.intensity,
            landed_count=new_landed,
            target_count=target,
            is_complete=is_complete,
            runtime_state=new_runtime_state,
            audio_base64=audio_base64,
            audio_content_type=audio_content_type,
            completion_metadata={
                "exercise_key": spec.key,
                "landed_count": new_landed,
                "target_count": target,
                "turn_count": new_turn_count,
                "completed_reason": (
                    "goal_reached" if goal_reached else "turn_cap" if capped else None
                ),
            },
        )

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _backend_key(task) -> str:
        rc = task.runtime_config or {}
        content = task.content or {}
        key = rc.get("backend_key") or content.get("exercise_key")
        if not key:
            raise ValueError(f"task {task.slug} has no runtime backend_key")
        return key

    @staticmethod
    def _target_count(task, spec: RoleplaySpec) -> int:
        content = task.content or {}
        target = content.get("target_count")
        return int(target) if isinstance(target, int) and target > 0 else spec.target_count

    @staticmethod
    def _sample_verbs(task) -> list[str]:
        rc = task.runtime_config or {}
        cfg = rc.get("verbs") or {}
        count = cfg.get("count") if isinstance(cfg, dict) else None
        count = count if isinstance(count, int) and count > 0 else _DEFAULT_VERB_COUNT
        verbs = word_list("verbs")
        return random.sample(verbs, min(count, len(verbs)))

    @staticmethod
    def _next_cursor(cursor: int, verbs: list[str]) -> int:
        if not verbs:
            return 0
        return (cursor + 1) % len(verbs)

    async def _synthesize(
        self, text: str, input: GenerateTaskInput
    ) -> tuple[str | None, str | None]:
        if not self._tts_enabled(input):
            return None, None
        return await self._synthesize_text(text)

    async def _synthesize_text(self, text: str) -> tuple[str | None, str | None]:
        if self._tts is None or not text:
            return None, None
        synth = await self._tts.synthesize(text, voice=self._tts_voice)
        if synth is None:
            return None, None
        return synth.audio_base64, synth.content_type

    def _tts_enabled(self, input: GenerateTaskInput) -> bool:
        if self._tts is None:
            return False
        type_meta = input.task_type.metadata or {}
        if type_meta.get("supports_tts") is False:
            return False
        tts_cfg = (input.task.runtime_config or {}).get("tts") or {}
        if tts_cfg.get("enabled") is False:
            return False
        return True
