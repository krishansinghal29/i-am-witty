from __future__ import annotations

from app.application.exceptions import ValidationError
from app.ports.integrations.transcription_provider import (
    EphemeralCredential,
    Transcript,
    TranscriptionProvider,
)


class TranscriptionService:
    """Mediates the speech-to-text provider for the attempt flow.

    The client streams audio directly to the provider and returns the
    transcript, which is authoritative: the backend mints the live credential
    and trusts the client transcript. It never transcribes audio itself.
    """

    def __init__(self, provider: TranscriptionProvider) -> None:
        self._provider = provider

    async def mint_ephemeral_credential(self) -> EphemeralCredential:
        return await self._provider.create_ephemeral_credential()

    def resolve_final_transcript(self, *, client_transcript: str | None) -> Transcript:
        if client_transcript and client_transcript.strip():
            return Transcript(text=client_transcript)
        raise ValidationError("no_transcript_source")
