"""Provider configuration for the roleplay prototype.

The `.env` file *is* the config file: it selects which chat / dictation / speech
provider is active and tunes each one. This module reads those env vars and
resolves them into typed provider objects, so the rest of the server never
touches raw env strings or hard-codes a vendor.

Selection (the two knobs you'll flip most):
    ROLEPLAY_CHAT       openai | sarvam          (default: openai)
    ROLEPLAY_DICTATION  deepgram | elevenlabs | sarvam   (default: deepgram)

All dictation is batch: the browser records the whole turn and the server
transcribes it in one shot, so the full sentence appears as soon as the user
stops speaking (no live word-by-word stream).

Secrets stay in env (each provider names the var holding its key), so nothing
secret is hard-coded here. Per-provider model/language overrides are optional;
sensible defaults preserve the original behaviour (Deepgram + GPT-5.3).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


def _clean(raw: str | None) -> str:
    """Trimmed env value, treating an all-comment value as unset.

    python-dotenv keeps an inline comment as the value when nothing precedes it
    (e.g. `KEY=   # note` -> "# note"), so a line meant to be blank isn't. Guard
    against that here so inline comments in `.env` can't leak into a value.
    """
    val = (raw or "").strip()
    return "" if val.startswith("#") else val


def _env(name: str, default: str = "") -> str:
    return _clean(os.environ.get(name)) or default


def _first(*names: str, default: str = "") -> str:
    """First non-empty value among env vars `names`, else `default`."""
    for n in names:
        val = _clean(os.environ.get(n))
        if val:
            return val
    return default


@dataclass(frozen=True)
class DictationProvider:
    name: str               # deepgram | elevenlabs | sarvam
    model: str
    language: str | None    # None => provider auto-detects
    api_key: str | None
    mode: str | None = None  # sarvam STT mode (e.g. "translit" for native romanized Hinglish)


@dataclass(frozen=True)
class ChatProvider:
    name: str               # openai | sarvam
    model: str              # litellm model string (e.g. "gpt-5.3-chat-latest", "openai/sarvam-30b")
    api_base: str | None    # custom OpenAI-compatible base (Sarvam), else None
    api_key: str | None     # explicit key; None => litellm reads it from env
    extra: dict[str, Any] = field(default_factory=dict)  # extra litellm kwargs (e.g. reasoning toggle)


@dataclass(frozen=True)
class SpeechProvider:
    name: str               # elevenlabs | sarvam
    model: str
    voice: str              # elevenlabs voice_id OR sarvam speaker
    language: str | None    # sarvam target_language_code (elevenlabs: None)
    sample_rate: int | None # sarvam speech_sample_rate (elevenlabs: None)
    api_key: str | None


@dataclass(frozen=True)
class Config:
    dictation: DictationProvider
    chat: ChatProvider
    gen_model: str          # model used for the first-impression blurb (chat creds reused)
    speech: SpeechProvider
    utterance_end_ms: int
    no_speech_end_ms: int
    system_prompt_override: str
    romanize: bool          # user wants Roman/Hinglish transcripts
    romanize_post: bool     # apply the /transliterate step (False when STT romanizes natively)
    romanize_key: str | None  # Sarvam key for the transliterate call


# --------------------------------------------------------------------------
# Resolvers
# --------------------------------------------------------------------------
def _resolve_dictation() -> DictationProvider:
    name = _env("ROLEPLAY_DICTATION", "deepgram").lower()

    if name == "elevenlabs":
        return DictationProvider(
            name="elevenlabs",
            model=_env("ROLEPLAY_ELEVENLABS_STT_MODEL", "scribe_v1"),
            language=_env("ROLEPLAY_ELEVENLABS_STT_LANGUAGE") or None,
            api_key=os.environ.get("ELEVENLABS_API_KEY"),
        )
    if name == "sarvam":
        # Sarvam STT output script depends on model + mode (both env-driven):
        #   saarika:v2.5              -> Devanagari transcription (default)
        #   saaras:v3 + mode=translit -> native romanized Hinglish in ONE call
        #   saaras:v3 (no mode)       -> translates to English
        # So for romanized Hinglish without the separate /transliterate step, set
        #   ROLEPLAY_SARVAM_STT_MODEL=saaras:v3  and  ROLEPLAY_SARVAM_STT_MODE=translit
        # (mode=translit is honored only on saaras:v3; saarika ignores it).
        return DictationProvider(
            name="sarvam",
            model=_env("ROLEPLAY_SARVAM_STT_MODEL", "saarika:v2.5"),
            # "unknown" => Sarvam auto-detects, which handles code-mixed Hinglish.
            language=_env("ROLEPLAY_SARVAM_STT_LANGUAGE", "unknown") or None,
            api_key=os.environ.get("SARVAM_API_KEY"),
            mode=_env("ROLEPLAY_SARVAM_STT_MODE") or None,
        )
    # default: deepgram (pre-recorded / batch transcription)
    return DictationProvider(
        name="deepgram",
        model=_env("ROLEPLAY_DEEPGRAM_MODEL", "nova-3"),
        language=_env("ROLEPLAY_DEEPGRAM_LANGUAGE", "en-US") or None,
        api_key=os.environ.get("DEEPGRAM_API_KEY"),
    )


def _resolve_chat() -> ChatProvider:
    name = _env("ROLEPLAY_CHAT", "openai").lower()

    if name == "sarvam":
        # sarvam-m is deprecated; current models are sarvam-30b / sarvam-105b.
        model = _env("ROLEPLAY_SARVAM_CHAT_MODEL", "sarvam-30b")
        # Route Sarvam's OpenAI-compatible endpoint through litellm's openai adapter.
        if "/" not in model:
            model = f"openai/{model}"
        # Sarvam models reason by default, which burns the whole token budget and
        # adds latency. For a spoken roleplay we disable it (reasoning_effort=null,
        # which must go through as a literal JSON null via extra_body). Set
        # ROLEPLAY_SARVAM_REASONING to low|medium|high to opt back in.
        effort = _env("ROLEPLAY_SARVAM_REASONING").lower()
        extra: dict[str, Any] = (
            {"reasoning_effort": effort}
            if effort in {"low", "medium", "high"}
            else {"extra_body": {"reasoning_effort": None}}
        )
        return ChatProvider(
            name="sarvam",
            model=model,
            api_base=_env("ROLEPLAY_SARVAM_API_BASE", "https://api.sarvam.ai/v1"),
            api_key=os.environ.get("SARVAM_API_KEY"),
            extra=extra,
        )
    # default: openai (GPT-5.3). litellm reads OPENAI_API_KEY from env itself.
    return ChatProvider(
        name="openai",
        model=_first(
            "ROLEPLAY_OPENAI_CHAT_MODEL",
            "ROLEPLAY_CHAT_MODEL",
            "LLM_GENERATOR_MODEL",
            default="gpt-5.3-chat-latest",
        ),
        api_base=None,
        api_key=None,
    )


def _resolve_speech() -> SpeechProvider:
    name = _env("ROLEPLAY_SPEECH", "elevenlabs").lower()

    if name == "sarvam":
        # Bulbul speaks code-mixed Hinglish naturally; hi-IN is the right locale.
        return SpeechProvider(
            name="sarvam",
            model=_env("ROLEPLAY_SARVAM_TTS_MODEL", "bulbul:v2"),
            voice=_env("ROLEPLAY_SARVAM_TTS_SPEAKER", "anushka"),
            language=_env("ROLEPLAY_SARVAM_TTS_LANGUAGE", "hi-IN"),
            sample_rate=int(_env("ROLEPLAY_SARVAM_TTS_SAMPLE_RATE", "22050")),
            api_key=os.environ.get("SARVAM_API_KEY"),
        )
    return SpeechProvider(
        name="elevenlabs",
        model=_first("ROLEPLAY_TTS_MODEL", default="eleven_flash_v2_5"),
        voice=_first("ROLEPLAY_VOICE_ID", default="21m00Tcm4TlvDq8ikWAM"),
        language=None,
        sample_rate=None,
        api_key=os.environ.get("ELEVENLABS_API_KEY"),
    )


def load() -> Config:
    chat = _resolve_chat()
    # First-impression blurb reuses the chat provider's credentials; only the
    # model string may be overridden independently.
    gen_model = _first("ROLEPLAY_GEN_MODEL", default=chat.model)
    if chat.name == "sarvam" and "/" not in gen_model:
        gen_model = f"openai/{gen_model}"

    romanize = _env("ROLEPLAY_ROMANIZE").lower() in {"1", "true", "yes", "on"}
    dictation = _resolve_dictation()
    # Skip the /transliterate step when the STT already romanized natively (Sarvam
    # translit mode); otherwise (ElevenLabs / Deepgram) we still post-process.
    romanize_post = romanize and dictation.mode != "translit"

    return Config(
        dictation=dictation,
        chat=chat,
        gen_model=gen_model,
        speech=_resolve_speech(),
        utterance_end_ms=int(_env("ROLEPLAY_UTTERANCE_END_MS", "2000")),
        no_speech_end_ms=int(_env("ROLEPLAY_NO_SPEECH_END_MS", "6000")),
        system_prompt_override=_env("ROLEPLAY_SYSTEM_PROMPT"),
        romanize=romanize,
        romanize_post=romanize_post,
        romanize_key=os.environ.get("SARVAM_API_KEY"),
    )
