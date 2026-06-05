from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.ports.integrations.transcription_provider import (
    EphemeralCredential,
    ProsodyMetadata,
    TranscribeInput,
    Transcript,
)


class FakeTranscriptionProvider:
    """Deterministic stand-in for the real (Deepgram) STT provider.

    Returns a fixed credential and a fixed transcript without decoding audio,
    touching the network, or loading any SDK.
    """

    async def create_ephemeral_credential(self) -> EphemeralCredential:
        """Return a fixed short-lived client credential."""
        return EphemeralCredential(
            token="fake-stt-ephemeral",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            provider="fake",
            extra={},
        )

    async def transcribe(self, input: TranscribeInput) -> Transcript:
        """Return a stable transcript, ignoring the submitted audio."""
        return Transcript(
            text="(fake transcript)",
            metadata=ProsodyMetadata(word_count=2, pause_count=0),
        )
