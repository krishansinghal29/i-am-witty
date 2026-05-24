from __future__ import annotations
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
import subprocess
import tempfile
from pathlib import Path
import openai
import config
from models import IngestedFile

_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

AUDIO_ONLY = {".mp3", ".wav", ".m4a"}
WHISPER_LIMIT = 25 * 1024 * 1024  # 25 MB


def _extract_audio(video_path: Path) -> Path:
    """Extract audio track to a temp MP3 at 64kbps (sufficient for speech)."""
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-vn", "-acodec", "mp3", "-ab", "64k", "-y", tmp.name],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return Path(tmp.name)


def transcribe_video(path: str | Path, output_transcripts_dir: str | Path) -> IngestedFile:
    path = Path(path)
    output_transcripts_dir = Path(output_transcripts_dir)
    output_transcripts_dir.mkdir(parents=True, exist_ok=True)

    file_type = "audio" if path.suffix.lower() in AUDIO_ONLY else "video"

    # Extract audio for video files, or for oversized audio files
    tmp_audio = None
    upload_path = path
    if file_type == "video" or path.stat().st_size > WHISPER_LIMIT:
        tmp_audio = _extract_audio(path)
        upload_path = tmp_audio

    try:
        with open(upload_path, "rb") as f:
            transcript = _client.audio.transcriptions.create(model="whisper-1", file=f)
    finally:
        if tmp_audio and tmp_audio.exists():
            tmp_audio.unlink()

    transcript_text = transcript.text

    out = {
        "filename": path.name,
        "file_type": file_type,
        "content": transcript_text,
        "metadata": {"source_path": str(path)},
    }
    (output_transcripts_dir / f"{path.stem}_transcript.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    return IngestedFile(
        filename=path.name,
        file_type=file_type,
        content=transcript_text,
        metadata={"source_path": str(path)},
    )
