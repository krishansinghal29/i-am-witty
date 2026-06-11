from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from app.ports.integrations.transcription_provider import EphemeralCredential

if TYPE_CHECKING:
    from deepgram import AsyncDeepgramClient

    from app.settings import Settings

# Short-lived JWT mechanism for the live/browser path. Deepgram's
# `POST /v1/auth/grant` returns a Bearer token (default 30s TTL, max 3600s)
# scoped to the core voice APIs only — never the Manage APIs.
# https://developers.deepgram.com/reference/auth/tokens/grant
_GRANT_ENDPOINT = "https://api.deepgram.com/v1/auth/grant"
_GRANT_TTL_SECONDS = 60


class DeepgramTranscriptionProvider:
    """Real Deepgram adapter implementing `TranscriptionProvider`.

    The backend holds the long-lived API key and mints a short-lived JWT via
    `/v1/auth/grant` so the client can stream microphone audio directly to
    Deepgram. The client-streamed transcript is authoritative; the backend
    does not transcribe audio itself.
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
