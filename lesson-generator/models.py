from __future__ import annotations

from dataclasses import dataclass, field, fields


@dataclass
class IngestedFile:
    filename: str
    file_type: str  # "text" | "html" | "video" | "audio"
    content: str
    # Timestamped transcript chunks: [{"start": float, "end": float, "text": str}]
    segments: list = field(default_factory=list)
    # 1-min (configurable) timeline hints: [{"timestamp": "MM:SS", "start_seconds": int, "text": str}]
    timeline: list = field(default_factory=list)
    # {"abstract": str, "key_points": [str, ...]} or None if not generated
    summary: dict | None = None
    metadata: dict = field(default_factory=dict)  # source_path, duration_seconds, language, etc.

    @classmethod
    def from_dict(cls, data: dict) -> "IngestedFile":
        """Build from a cached JSON dict, ignoring any unknown keys (forward-compatible)."""
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class ScriptSegment:
    heading: str
    text: str  # includes [pause], [short pause], [long pause] markers
    speaker_notes: str = ""


@dataclass
class LessonScript:
    title: str
    estimated_duration_secs: int
    segments: list[ScriptSegment]
    raw_text: str  # full concatenated script with pause markers for ElevenLabs


@dataclass
class AudioOutput:
    file_path: str
    voice_id: str
    duration_secs: float = 0.0
