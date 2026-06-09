from __future__ import annotations

import logging

from app.infrastructure.runtime.prompts.registry import get_exercise_spec
from app.ports.integrations.llm_provider import LlmProvider
from app.ports.integrations.tts_provider import TtsProvider
from app.ports.task_runtime_engine import (
    AssignedTechnique,
    CompleteTaskRuntimeInput,
    GeneratedPrompt,
    GeneratedTaskPayload,
    GenerateTaskInput,
    PromptMessage,
    TaskRuntimeResult,
)

logger = logging.getLogger(__name__)

# The generator favours variety; the evaluator favours consistency. These match
# the legacy backend's effective settings (creative generation, temperature 1.0
# evaluation).
_GENERATION_TEMPERATURE = 1.0
_EVALUATION_TEMPERATURE = 1.0


class VoicePromptTaskEngine:
    """LLM-backed `TaskRuntimeEngine` for all `voice_prompt_v1` task types.

    A single engine serves `voice_single_prompt`, `voice_dialogue_prompt`, and
    `voice_scaffolded_prompt`: it routes to the exercise prompt bundle by the
    task's ``runtime_config.backend_key`` and reads its shape (assigned
    technique, scaffold stages, dialogue vs single) from the task's ``content``
    and ``runtime_config``. Generation and evaluation are the two external LLM
    calls; both run outside any DB transaction (the services release the read
    transaction before calling `complete`).
    """

    def __init__(
        self,
        llm: LlmProvider,
        tts: TtsProvider | None = None,
        *,
        generator_model: str | None = None,
        evaluator_model: str | None = None,
        tts_voice: str | None = None,
    ) -> None:
        self._llm = llm
        self._tts = tts
        self._generator_model = generator_model
        self._evaluator_model = evaluator_model
        self._tts_voice = tts_voice

    async def generate(self, input: GenerateTaskInput) -> GeneratedTaskPayload:
        spec = get_exercise_spec(self._backend_key(input.task))

        result = await self._llm.complete_structured(
            messages=[
                {"role": "system", "content": spec.generator_system},
                {"role": "user", "content": spec.generator_prompt()},
            ],
            response_model=spec.generator_response_schema,
            temperature=_GENERATION_TEMPERATURE,
            model=self._generator_model,
        )
        raw_messages = result.model_dump()["messages"]
        messages = tuple(
            PromptMessage(role=m["role"], content=m["content"]) for m in raw_messages
        )

        technique: AssignedTechnique | None = None
        if spec.technique_picker is not None:
            picked = spec.technique_picker()
            if picked:
                technique = AssignedTechnique(
                    name=picked["name"],
                    instruction=picked["instruction"],
                    example=picked["example"],
                )

        speech_text = self._build_speech_text(raw_messages)

        audio_base64: str | None = None
        audio_content_type: str | None = None
        if speech_text and self._tts_enabled(input):
            synth = await self._tts.synthesize(speech_text, voice=self._tts_voice)
            if synth is not None:
                audio_base64 = synth.audio_base64
                audio_content_type = synth.content_type

        return GeneratedTaskPayload(
            prompt=GeneratedPrompt(messages=messages, speech_text=speech_text),
            assigned_technique=technique,
            scaffold_stages=self._scaffold_stages(input.task),
            audio_base64=audio_base64,
            audio_content_type=audio_content_type,
            avatar_image_url=None,
        )

    async def complete(
        self, input: CompleteTaskRuntimeInput
    ) -> TaskRuntimeResult:
        backend_key = self._backend_key(input.task)
        spec = get_exercise_spec(backend_key)

        question_data = [
            {"role": m.role, "content": m.content} for m in input.prompt_messages
        ]
        technique_name = (
            input.assigned_technique.name if input.assigned_technique else None
        )

        prompt_text = spec.evaluator_prompt(
            question_data=question_data,
            transcription=input.transcript,
            technique_name=technique_name,
        )

        try:
            result = await self._llm.complete_structured(
                messages=[
                    {"role": "system", "content": spec.evaluator_system},
                    {"role": "user", "content": prompt_text},
                ],
                response_model=spec.evaluator_response_schema,
                temperature=_EVALUATION_TEMPERATURE,
                model=self._evaluator_model,
            )
            data = result.model_dump()
        except Exception as exc:
            logger.error("Evaluation failed for %s: %s", backend_key, exc)
            data = spec.evaluator_fallback()

        rc = input.task.runtime_config or {}
        return TaskRuntimeResult(
            style_label=None,
            feedback_html=data["feedback"],
            sample_answer_html=data["sample_answer"],
            completion_metadata={
                "exercise_key": backend_key,
                "evaluator_version": rc.get("prompt_bundle_key"),
                "assigned_technique_name": technique_name,
            },
        )

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _backend_key(task) -> str:
        """Resolve the prompt-bundle key from runtime_config (or content)."""
        rc = task.runtime_config or {}
        content = task.content or {}
        key = rc.get("backend_key") or content.get("exercise_key")
        if not key:
            raise ValueError(f"task {task.slug} has no runtime backend_key")
        return key

    @staticmethod
    def _scaffold_stages(task) -> tuple[dict, ...]:
        content = task.content or {}
        stages = content.get("scaffold_stages")
        return tuple(stages) if isinstance(stages, list) else ()

    @staticmethod
    def _build_speech_text(raw_messages: list[dict]) -> str:
        """Build the spoken text: bare line for single, role-labelled for dialogue."""
        parts = [
            (m.get("role", ""), m.get("content", ""))
            for m in raw_messages
            if m.get("content")
        ]
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0][1]
        return "\n".join(
            f"{role}: {content}" if role else content for role, content in parts
        )

    def _tts_enabled(self, input: GenerateTaskInput) -> bool:
        """TTS runs eagerly when a provider exists and nothing opts out.

        Honours the task type's ``supports_tts`` metadata and an optional
        ``runtime_config.tts.enabled`` per-task kill switch.
        """
        if self._tts is None:
            return False
        type_meta = input.task_type.metadata or {}
        if type_meta.get("supports_tts") is False:
            return False
        tts_cfg = (input.task.runtime_config or {}).get("tts") or {}
        if tts_cfg.get("enabled") is False:
            return False
        return True
