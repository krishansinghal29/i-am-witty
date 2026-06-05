from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class EphemeralCredential:
    """Short-lived client credential for the live-transcript path.

    The backend holds the real provider key; this narrowly-scoped token lets
    the client stream directly to the provider for low latency. A
    non-streaming provider may return a no-op credential (empty token); the
    client then falls back to typed input without losing correctness.
    """

    token: str
    expires_at: datetime | None
    provider: str
    extra: dict


@dataclass(frozen=True)
class TranscribeInput:
    audio_base64: str
    content_type: str
    language: str | None = None


@dataclass(frozen=True)
class ProsodyMetadata:
    """Optional, provider-dependent prosody signals.

    Evaluation must NOT depend on these; they are informational only and may
    be absent for providers that do not report them.
    """

    word_count: int | None = None
    pause_count: int | None = None


@dataclass(frozen=True)
class Transcript:
    text: str
    metadata: ProsodyMetadata | None = None


class TranscriptionProvider(Protocol):
    """Swappable speech-to-text provider (Deepgram today).

    The backend is the authority for the transcript that gets evaluated and
    stored, and the provider key lives only on the backend. Two
    responsibilities: mint a short-lived client credential for the live path,
    and produce the authoritative final transcript from submitted audio.
    """

    async def create_ephemeral_credential(self) -> EphemeralCredential:
        """Mint a short-lived, narrowly-scoped client credential.

        A non-streaming provider can return a no-op credential.
        """
        ...

    async def transcribe(self, input: TranscribeInput) -> Transcript:
        """Batch-transcribe submitted answer audio into the final transcript.

        Returns text plus optional prosody metadata when the provider supports
        it; callers must treat that metadata as optional.
        """
        ...
