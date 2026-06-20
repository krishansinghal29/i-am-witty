"""Env -> typed STT/TTS provider config (adapted from the old server). [P9.5]"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    val = (os.environ.get(name) or "").strip()
    return default if (not val or val.startswith("#")) else val


@dataclass(frozen=True)
class DictationProvider:
    name: str               # deepgram | elevenlabs | sarvam
    model: str
    language: str | None
    api_key: str | None
    mode: str | None = None


@dataclass(frozen=True)
class SpeechProvider:
    name: str               # elevenlabs | sarvam
    model: str
    voice: str
    language: str | None
    sample_rate: int | None
    api_key: str | None


def load_dictation() -> DictationProvider:
    name = _env("ROLEPLAY_DICTATION", "deepgram").lower()
    if name == "elevenlabs":
        return DictationProvider("elevenlabs", _env("ROLEPLAY_ELEVENLABS_STT_MODEL", "scribe_v1"),
                                 _env("ROLEPLAY_ELEVENLABS_STT_LANGUAGE") or None,
                                 os.environ.get("ELEVENLABS_API_KEY"))
    if name == "sarvam":
        return DictationProvider("sarvam", _env("ROLEPLAY_SARVAM_STT_MODEL", "saarika:v2.5"),
                                 _env("ROLEPLAY_SARVAM_STT_LANGUAGE", "unknown") or None,
                                 os.environ.get("SARVAM_API_KEY"),
                                 _env("ROLEPLAY_SARVAM_STT_MODE") or None)
    return DictationProvider("deepgram", _env("ROLEPLAY_DEEPGRAM_MODEL", "nova-3"),
                             _env("ROLEPLAY_DEEPGRAM_LANGUAGE", "en-US") or None,
                             os.environ.get("DEEPGRAM_API_KEY"))


def load_speech() -> SpeechProvider:
    name = _env("ROLEPLAY_SPEECH", "elevenlabs").lower()
    if name == "sarvam":
        return SpeechProvider("sarvam", _env("ROLEPLAY_SARVAM_TTS_MODEL", "bulbul:v2"),
                              _env("ROLEPLAY_SARVAM_TTS_SPEAKER", "anushka"),
                              _env("ROLEPLAY_SARVAM_TTS_LANGUAGE", "hi-IN"),
                              int(_env("ROLEPLAY_SARVAM_TTS_SAMPLE_RATE", "22050")),
                              os.environ.get("SARVAM_API_KEY"))
    return SpeechProvider("elevenlabs", _env("ROLEPLAY_TTS_MODEL", "eleven_flash_v2_5"),
                          _env("ROLEPLAY_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
                          None, None, os.environ.get("ELEVENLABS_API_KEY"))
