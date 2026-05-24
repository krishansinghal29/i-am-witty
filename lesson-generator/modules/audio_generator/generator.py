from __future__ import annotations
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import tempfile
from pathlib import Path

from elevenlabs import ElevenLabs

import config
from models import AudioOutput, LessonScript


def generate_audio(
    script: LessonScript,
    output_audio_dir: str | Path,
    voice_id: str | None = None,
    filename: str = "lesson.mp3",
) -> AudioOutput:
    used_voice_id = voice_id or config.ELEVENLABS_VOICE_ID
    output_audio_dir = Path(output_audio_dir)
    output_audio_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_audio_dir / filename

    client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        voice_id=used_voice_id,
        model_id="eleven_v3",
        text=script.raw_text,
    )

    # Write to a temp file first; only rename to final path on success so a
    # failed run never leaves a zero-byte file that poisons the cache.
    tmp = tempfile.NamedTemporaryFile(dir=output_audio_dir, delete=False, suffix=".mp3")
    try:
        with open(tmp.name, "wb") as f:
            if isinstance(audio, bytes):
                f.write(audio)
            else:
                for chunk in audio:
                    f.write(chunk)
        Path(tmp.name).replace(output_path)
    except Exception:
        Path(tmp.name).unlink(missing_ok=True)
        raise

    return AudioOutput(file_path=str(output_path), voice_id=used_voice_id)
