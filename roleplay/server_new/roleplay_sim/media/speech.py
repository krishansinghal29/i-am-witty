"""Text-to-speech (ported/adapted from the old server). [P9.5]

Sarvam Bulbul is a batch JSON call returning base64 WAV (handled here). ElevenLabs
is streaming MP3 (helper returns the streaming context for the API to passthrough).
"""
from __future__ import annotations

import base64
import logging

import httpx

from roleplay_sim.media.providers import SpeechProvider

logger = logging.getLogger("roleplay.speech")

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"


class SpeechError(RuntimeError):
    """Raised when the TTS provider rejects or fails the request."""


async def synthesize_sarvam(provider: SpeechProvider, text: str, http: httpx.AsyncClient) -> bytes:
    payload: dict[str, object] = {
        "text": text,
        "target_language_code": provider.language or "hi-IN",
        "speaker": provider.voice,
        "model": provider.model,
    }
    if provider.sample_rate:
        payload["speech_sample_rate"] = provider.sample_rate
    r = await http.post(SARVAM_TTS_URL,
                        headers={"api-subscription-key": provider.api_key,
                                 "content-type": "application/json"}, json=payload)
    if r.status_code != 200:
        detail = r.text[:300]
        logger.error("sarvam tts %s: %s", r.status_code, detail)
        raise SpeechError(f"sarvam_tts_{r.status_code}: {detail}")
    audios = r.json().get("audios") or []
    if not audios:
        raise SpeechError("sarvam_tts_empty")
    return base64.b64decode(audios[0])


def elevenlabs_stream_request(provider: SpeechProvider, text: str):
    """Return (url, headers, payload) for an ElevenLabs streaming TTS request."""
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{provider.voice}/stream"
           "?output_format=mp3_44100_128&optimize_streaming_latency=3")
    headers = {"xi-api-key": provider.api_key or "", "content-type": "application/json"}
    payload = {"text": text, "model_id": provider.model,
               "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}}
    return url, headers, payload
