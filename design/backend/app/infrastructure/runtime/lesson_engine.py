from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

from app.ports.task_runtime_engine import (
    CaptionCue,
    CompleteTaskRuntimeInput,
    GeneratedPrompt,
    GeneratedTaskPayload,
    GenerateTaskInput,
    TaskRuntimeResult,
    TurnResult,
    TurnTaskRuntimeInput,
)

logger = logging.getLogger(__name__)

# Per-lesson transcript + time-aligned caption cues, produced offline by the
# forced-alignment pass and committed as static resources. The engine reads
# them at generate time; a missing file degrades gracefully to "no captions".
_CAPTIONS_DIR = Path(__file__).parent / "lessons" / "captions"


@lru_cache(maxsize=64)
def _load_caption_resource(audio_key: str) -> tuple[str | None, tuple[CaptionCue, ...]]:
    """Load `(transcript, cues)` for a lesson from its committed JSON resource.

    The file shape is ``{"transcript": str, "cues": [{"start","end","text"}]}``.
    Cached per key (the files are immutable at runtime). Returns ``(None, ())``
    when the resource is absent or malformed so a lesson still plays its audio
    before the alignment data lands.
    """
    path = _CAPTIONS_DIR / f"{audio_key}.json"
    if not path.exists():
        return None, ()
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        logger.warning("lesson caption resource unreadable: %s", path)
        return None, ()

    transcript = data.get("transcript")
    transcript = transcript if isinstance(transcript, str) and transcript else None

    cues: list[CaptionCue] = []
    for raw in data.get("cues") or []:
        if not isinstance(raw, dict):
            continue
        try:
            cues.append(
                CaptionCue(
                    start=float(raw["start"]),
                    end=float(raw["end"]),
                    text=str(raw["text"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return transcript, tuple(cues)


class LessonTaskEngine:
    """`TaskRuntimeEngine` for ``lesson_v1`` tasks: a pre-recorded audio lesson.

    Unlike the LLM-backed engines this does no generation, transcription, or
    scoring — ``generate`` is a pure, instant assembly of the hosted audio URL
    plus its committed transcript/captions. A lesson has nothing to evaluate, so
    ``complete`` returns an empty result (the service drives lesson completion
    through its light, non-metered finalize path) and ``turn`` is unsupported.
    """

    def __init__(self, *, audio_base_url: str) -> None:
        self._audio_base_url = audio_base_url.rstrip("/")

    async def generate(self, input: GenerateTaskInput) -> GeneratedTaskPayload:
        audio_key = self._audio_key(input.task)
        audio_url = f"{self._audio_base_url}/{audio_key}.mp3"

        transcript, captions = _load_caption_resource(audio_key)
        # The seeded `content.transcript` is a fallback for lessons whose
        # alignment resource is not committed yet.
        if transcript is None:
            seeded = (input.task.content or {}).get("transcript")
            transcript = seeded if isinstance(seeded, str) and seeded else None

        return GeneratedTaskPayload(
            prompt=GeneratedPrompt(messages=(), speech_text=None),
            audio_url=audio_url,
            transcript=transcript,
            captions=captions,
        )

    async def complete(self, input: CompleteTaskRuntimeInput) -> TaskRuntimeResult:
        # Lessons are consumption, not practice: there is no transcript to grade
        # and no feedback to render. Completion side-effects (marking "listened")
        # run in the service's light finalize, not here.
        return TaskRuntimeResult(
            style_label=None,
            feedback_html="",
            sample_answer_html="",
            completion_metadata={
                "kind": "lesson",
                "audio_key": self._audio_key(input.task),
            },
        )

    async def turn(self, input: TurnTaskRuntimeInput) -> TurnResult:
        raise NotImplementedError("lesson tasks are not conversational")

    @staticmethod
    def _audio_key(task) -> str:
        """The stem of the hosted mp3 (and caption resource) for this lesson.

        Sourced from ``content.audio_key`` (e.g. ``pushPull``); falls back to the
        legacy ``exercise_key`` so a lesson can reuse an exercise's audio naming.
        """
        content = task.content or {}
        key = content.get("audio_key") or content.get("exercise_key")
        if not key:
            raise ValueError(f"lesson task {task.slug} has no audio_key")
        return str(key)
