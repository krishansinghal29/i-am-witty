"""Batch text-to-speech providers.

ElevenLabs streams MP3 and is handled inline in `main.py` (it stays a
StreamingResponse). Sarvam's Bulbul TTS is a batch JSON call that returns the
clip as base64 WAV, so it lives here: synthesize one phrase, decode, hand back
the WAV bytes. The client plays each phrase's audio as a complete blob either
way, so non-streaming Sarvam slots in without client changes.
"""

from __future__ import annotations

import base64
import logging

import httpx

from server.config import SpeechProvider

logger = logging.getLogger("roleplay.speech")

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"


class SpeechError(RuntimeError):
    """Raised when the TTS provider rejects or fails the request."""


async def synthesize_sarvam(provider: SpeechProvider, text: str, http: httpx.AsyncClient) -> bytes:
    """Synthesize `text` with Sarvam Bulbul; return WAV bytes."""
    payload: dict[str, object] = {
        "text": text,
        "target_language_code": provider.language or "hi-IN",
        "speaker": provider.voice,
        "model": provider.model,
    }
    if provider.sample_rate:
        payload["speech_sample_rate"] = provider.sample_rate
    r = await http.post(
        SARVAM_TTS_URL,
        headers={
            "api-subscription-key": provider.api_key,
            "content-type": "application/json",
        },
        json=payload,
    )
    if r.status_code != 200:
        detail = r.text[:300]
        logger.error("sarvam tts %s: %s", r.status_code, detail)
        raise SpeechError(f"sarvam_tts_{r.status_code}: {detail}")
    audios = r.json().get("audios") or []
    if not audios:
        raise SpeechError("sarvam_tts_empty")
    return base64.b64decode(audios[0])
