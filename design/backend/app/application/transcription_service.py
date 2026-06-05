from __future__ import annotations

from app.application.exceptions import ValidationError
from app.ports.integrations.transcription_provider import (
    EphemeralCredential,
    TranscribeInput,
    Transcript,
    TranscriptionProvider,
)


class TranscriptionService:
    """Mediates the speech-to-text provider for the attempt flow.

    The backend is the authority for the final transcript: submitted audio is
    always transcribed server-side, and a client-supplied transcript is only
    trusted when no audio is available.
    """

    def __init__(self, provider: TranscriptionProvider) -> None:
        self._provider = provider

    async def mint_ephemeral_credential(self) -> EphemeralCredential:
        return await self._provider.create_ephemeral_credential()

    async def resolve_final_transcript(
        self,
        *,
        client_transcript: str | None = None,
        audio_base64: str | None = None,
        content_type: str | None = None,
        language: str | None = None,
    ) -> Transcript:
        if audio_base64:
            return await self._provider.transcribe(
                TranscribeInput(
                    audio_base64=audio_base64,
                    content_type=content_type or "audio/webm",
                    language=language,
                )
            )
        if client_transcript and client_transcript.strip():
            return Transcript(text=client_transcript)
        raise ValidationError("no_transcript_source")
