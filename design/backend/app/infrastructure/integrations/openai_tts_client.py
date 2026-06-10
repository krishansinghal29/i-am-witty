from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

from app.ports.integrations.tts_provider import SynthesizedSpeech

if TYPE_CHECKING:
    from openai import AsyncOpenAI

    from app.settings import Settings

logger = logging.getLogger(__name__)

_MODEL = "tts-1"
_DEFAULT_VOICE = "nova"
_CONTENT_TYPE = "audio/mpeg"


class OpenAiTtsProvider:
    """OpenAI text-to-speech adapter implementing `TtsProvider`.

    Builds the async SDK client lazily so the module imports without the SDK or
    a key present. Returns ``None`` (never raises) when TTS is unconfigured or
    the call fails, keeping the spoken prompt strictly optional.
    """

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.openai_api_key
        self._voice = settings.tts_voice or _DEFAULT_VOICE
        self._timeout = settings.tts_request_timeout_seconds
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI | None:
        if not self._api_key:
            return None
        if self._client is None:
            from openai import AsyncOpenAI

            # Without an explicit timeout the SDK waits its 600s default on a
            # stalled response; TTS is best-effort so we fail fast and fall back
            # to text instead of holding the generate request open.
            self._client = AsyncOpenAI(api_key=self._api_key, timeout=self._timeout)
        return self._client

    async def synthesize(
        self, text: str, *, voice: str | None = None
    ) -> SynthesizedSpeech | None:
        if not text or not text.strip():
            return None
        client = self._get_client()
        if client is None:
            return None
        try:
            response = await client.audio.speech.create(
                model=_MODEL,
                voice=voice or self._voice,
                input=text,
            )
            audio_bytes = response.content
            return SynthesizedSpeech(
                audio_base64=base64.b64encode(audio_bytes).decode("utf-8"),
                content_type=_CONTENT_TYPE,
            )
        except Exception as exc:  # best-effort; prompt text is always shown
            logger.warning("OpenAI TTS failed (non-fatal): %s", exc)
            return None
