"""Batch speech-to-text (ported/adapted from the old server). [P9.5]

The browser records a whole turn, POSTs WAV; the active provider transcribes it in
one shot. `romanize` transliterates Devanagari to Hinglish when needed.
"""
from __future__ import annotations

import logging
import re

import httpx

from roleplay_sim.media.providers import DictationProvider

logger = logging.getLogger("roleplay.dictation")

DEEPGRAM_STT_URL = "https://api.deepgram.com/v1/listen"
ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TRANSLITERATE_URL = "https://api.sarvam.ai/transliterate"

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_BRACKET_TAG = re.compile(r"\s*[(\[][^)\]]*[)\]]\s*")


class TranscriptionError(RuntimeError):
    """Raised when the active provider rejects or fails the request."""


def _strip_bracket_tags(text: str) -> str:
    return _BRACKET_TAG.sub(" ", text).strip()


def _raise_for_status(name: str, r: httpx.Response) -> None:
    if r.status_code != 200:
        detail = r.text[:300]
        logger.error("%s stt %s: %s", name, r.status_code, detail)
        raise TranscriptionError(f"{name}_stt_{r.status_code}: {detail}")


async def transcribe(provider: DictationProvider, audio: bytes, http: httpx.AsyncClient) -> str:
    if not provider.api_key:
        raise TranscriptionError(f"{provider.name}_not_configured")
    if provider.name == "deepgram":
        return await _deepgram(provider, audio, http)
    if provider.name == "elevenlabs":
        return await _elevenlabs(provider, audio, http)
    if provider.name == "sarvam":
        return await _sarvam(provider, audio, http)
    raise TranscriptionError(f"unsupported_provider:{provider.name}")


async def _deepgram(provider, audio, http):
    params = {"model": provider.model, "smart_format": "true", "punctuate": "true"}
    if provider.language:
        params["language"] = provider.language
    r = await http.post(DEEPGRAM_STT_URL, params=params,
                        headers={"Authorization": f"Token {provider.api_key}",
                                 "Content-Type": "audio/wav"}, content=audio)
    _raise_for_status("deepgram", r)
    alts = r.json().get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])
    return ((alts[0].get("transcript") or "") if alts else "").strip()


async def _elevenlabs(provider, audio, http):
    data = {"model_id": provider.model, "tag_audio_events": "false"}
    if provider.language:
        data["language_code"] = provider.language
    r = await http.post(ELEVENLABS_STT_URL, headers={"xi-api-key": provider.api_key},
                        data=data, files={"file": ("turn.wav", audio, "audio/wav")})
    _raise_for_status("elevenlabs", r)
    return _strip_bracket_tags(r.json().get("text") or "")


async def _sarvam(provider, audio, http):
    data = {"model": provider.model}
    if provider.language:
        data["language_code"] = provider.language
    if provider.mode:
        data["mode"] = provider.mode
    r = await http.post(SARVAM_STT_URL, headers={"api-subscription-key": provider.api_key},
                        data=data, files={"file": ("turn.wav", audio, "audio/wav")})
    _raise_for_status("sarvam", r)
    return (r.json().get("transcript") or "").strip()


async def romanize(text: str, api_key: str | None, http: httpx.AsyncClient) -> str:
    """Best-effort Devanagari -> Roman (Hinglish); no-op for English-only text."""
    if not text or not api_key or not _DEVANAGARI.search(text):
        return text
    try:
        r = await http.post(SARVAM_TRANSLITERATE_URL,
                            headers={"api-subscription-key": api_key, "content-type": "application/json"},
                            json={"input": text, "source_language_code": "hi-IN",
                                  "target_language_code": "en-IN"})
        if r.status_code == 200:
            return (r.json().get("transliterated_text") or text).strip()
        logger.error("transliterate %s: %s", r.status_code, r.text[:200])
    except Exception:
        logger.exception("romanize failed")
    return text
