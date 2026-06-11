from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class EphemeralCredential:
    """Short-lived client credential for the live-transcript path.

    The backend holds the real provider key; this narrowly-scoped token lets
    the client stream microphone audio directly to the provider for low
    latency. The transcript the client streams back is authoritative — the
    backend does not re-transcribe.
    """

    token: str
    expires_at: datetime | None
    provider: str
    extra: dict


@dataclass(frozen=True)
class Transcript:
    text: str


class TranscriptionProvider(Protocol):
    """Swappable speech-to-text provider (Deepgram today).

    The provider key lives only on the backend. Its sole responsibility is to
    mint a short-lived client credential so the client can stream audio
    directly to the provider; the client-streamed transcript is authoritative,
    so the backend never transcribes audio itself.
    """

    async def create_ephemeral_credential(self) -> EphemeralCredential:
        """Mint a short-lived, narrowly-scoped client credential."""
        ...
