from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from app.ports.integrations.transcription_provider import (
    EphemeralCredential,
    ProsodyMetadata,
    TranscribeInput,
    Transcript,
)

if TYPE_CHECKING:
    from deepgram import AsyncDeepgramClient

    from app.settings import Settings

# Short-lived JWT mechanism for the live/browser path. Deepgram's
# `POST /v1/auth/grant` returns a Bearer token (default 30s TTL, max 3600s)
# scoped to the core voice APIs only — never the Manage APIs.
# https://developers.deepgram.com/reference/auth/tokens/grant
_GRANT_ENDPOINT = "https://api.deepgram.com/v1/auth/grant"
_GRANT_TTL_SECONDS = 60
_DEFAULT_MODEL = "nova-3"


class DeepgramTranscriptionProvider:
    """Real Deepgram speech-to-text adapter implementing `TranscriptionProvider`.

    The backend holds the long-lived API key. For the live path it mints a
    short-lived JWT via `/v1/auth/grant` so the client can stream directly; for
    submitted answers it runs pre-recorded transcription and returns the
    authoritative transcript.
    """

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.deepgram_api_key
        self._project_id = settings.deepgram_project_id
        self._client: AsyncDeepgramClient | None = None

    def _require_key(self) -> str:
        if not self._api_key:
            raise RuntimeError("deepgram_not_configured")
        return self._api_key

    def _get_client(self) -> AsyncDeepgramClient:
        """Build the async SDK client lazily so the module imports without creds."""
        if self._client is None:
            from deepgram import AsyncDeepgramClient

            self._client = AsyncDeepgramClient(api_key=self._require_key())
        return self._client

    async def create_ephemeral_credential(self) -> EphemeralCredential:
        self._require_key()
        client = self._get_client()
        response = await client.auth.v1.tokens.grant(ttl_seconds=_GRANT_TTL_SECONDS)
        ttl_seconds = int(getattr(response, "expires_in", None) or _GRANT_TTL_SECONDS)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        return EphemeralCredential(
            token=response.access_token,
            expires_at=expires_at,
            provider="deepgram",
            extra={
                "ttl_seconds": ttl_seconds,
                "auth_scheme": "Bearer",
                "grant_endpoint": _GRANT_ENDPOINT,
            },
        )

    async def transcribe(self, input: TranscribeInput) -> Transcript:
        self._require_key()
        client = self._get_client()
        audio = base64.b64decode(input.audio_base64)
        # The audio mime type rides on the request's Content-Type header.
        response = await client.listen.v1.media.transcribe_file(
            request=audio,
            model=_DEFAULT_MODEL,
            smart_format=True,
            language=input.language,
            request_options={
                "additional_headers": {"Content-Type": input.content_type}
            },
        )
        text, word_count = _best_alternative(response)
        return Transcript(
            text=text,
            metadata=ProsodyMetadata(word_count=word_count, pause_count=None),
        )


def _best_alternative(response: object) -> tuple[str, int | None]:
    """Pull the top transcript and its word count from a Deepgram response.

    Defensive against missing fields so an empty/odd response degrades to an
    empty transcript rather than raising.
    """
    results = getattr(response, "results", None)
    channels = getattr(results, "channels", None) or []
    if not channels:
        return "", None
    alternatives = getattr(channels[0], "alternatives", None) or []
    if not alternatives:
        return "", None
    best = alternatives[0]
    text = getattr(best, "transcript", "") or ""
    words = getattr(best, "words", None)
    word_count = len(words) if words is not None else None
    return text, word_count
