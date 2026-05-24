from dataclasses import dataclass, field


@dataclass
class IngestedFile:
    filename: str
    file_type: str  # "text" | "html" | "video" | "audio"
    content: str
    metadata: dict = field(default_factory=dict)  # word_count, duration_seconds, etc.


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
