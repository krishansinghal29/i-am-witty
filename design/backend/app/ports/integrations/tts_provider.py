from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SynthesizedSpeech:
    audio_base64: str
    content_type: str


class TtsProvider(Protocol):
    """Swappable text-to-speech provider for spoken prompts.

    TTS is best-effort: the spoken prompt is an enhancement on top of the
    always-visible prompt text, so `synthesize` returns ``None`` on any failure
    rather than raising, and callers degrade to text/client-side speech.
    """

    async def synthesize(
        self, text: str, *, voice: str | None = None
    ) -> SynthesizedSpeech | None:
        ...
