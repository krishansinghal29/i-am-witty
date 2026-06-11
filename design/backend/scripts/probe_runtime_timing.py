"""Ad-hoc latency probe for the 'start practice' (get_task_runtime) flow.

Times each external phase independently so we can see where the 15-20s goes:
  1. litellm import (one-time per process)
  2. LLM generation call (structured output, push_pull spec)
  3. TTS synthesize call

Run: .venv/bin/python scripts/probe_runtime_timing.py
"""
from __future__ import annotations

import asyncio
import time

from app.settings import get_settings
from app.infrastructure.runtime.prompts.registry import get_exercise_spec


async def main() -> None:
    settings = get_settings()
    print(f"generator_model = {settings.llm_generator_model}")
    print(f"evaluator_model = {settings.llm_evaluator_model}")
    print(f"llm_timeout     = {settings.llm_request_timeout_seconds}  retries={settings.llm_num_retries}")
    print(f"tts_voice       = {settings.tts_voice}  tts_timeout={settings.tts_request_timeout_seconds}")
    print(f"openai_key set  = {bool(settings.openai_api_key)}")
    print("-" * 60)

    t = time.perf_counter()
    import litellm  # noqa: F401
    print(f"[import litellm]           {time.perf_counter() - t:6.2f}s")

    from app.infrastructure.integrations.litellm_provider import LiteLlmProvider
    from app.infrastructure.integrations.openai_tts_client import OpenAiTtsProvider

    llm = LiteLlmProvider(settings, default_model=settings.llm_generator_model)
    tts = OpenAiTtsProvider(settings)

    spec = get_exercise_spec("pushPull")
    gen_messages = [
        {"role": "system", "content": spec.generator_system},
        {"role": "user", "content": spec.generator_prompt()},
    ]

    # Run the generation call 3x to separate cold vs warm latency.
    speech_text = ""
    for i in range(3):
        t = time.perf_counter()
        result = await llm.complete_structured(
            messages=gen_messages,
            response_model=spec.generator_response_schema,
            temperature=1.0,
            model=settings.llm_generator_model,
        )
        dt = time.perf_counter() - t
        msgs = result.model_dump()["messages"]
        speech_text = msgs[0]["content"]
        print(f"[LLM generate call #{i+1}]    {dt:6.2f}s  -> {speech_text!r}")

    # TTS of the generated sentence, 2x.
    for i in range(2):
        t = time.perf_counter()
        synth = await tts.synthesize(speech_text, voice=settings.tts_voice)
        dt = time.perf_counter() - t
        size = len(synth.audio_base64) if synth else 0
        print(f"[TTS synthesize #{i+1}]       {dt:6.2f}s  (b64 len={size})")


if __name__ == "__main__":
    asyncio.run(main())
