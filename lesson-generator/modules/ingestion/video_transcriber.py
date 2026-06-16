from __future__ import annotations
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
import subprocess
import tempfile
from pathlib import Path

import openai

import config
from models import IngestedFile
from modules.ingestion.timeline import build_timeline, format_timestamp
from modules.ingestion.summarizer import summarize_transcript

_client = openai.OpenAI(api_key=config.OPENAI_API_KEY, max_retries=6)

AUDIO_ONLY = {".mp3", ".wav", ".m4a"}
WHISPER_LIMIT = 25 * 1024 * 1024  # 25 MB hard limit on the Whisper endpoint
# 64 kbps mono mp3 ≈ 0.48 MB/min, so 20 min ≈ 9.6 MB — safely under the limit.
CHUNK_SECONDS = 20 * 60


def _extract_audio(video_path: Path) -> Path:
    """Extract audio to a temp 64 kbps mono MP3 (small, plenty for speech)."""
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-vn", "-ac", "1", "-acodec", "mp3", "-ab", "64k", "-y", tmp.name],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return Path(tmp.name)


def _split_audio(audio_path: Path, chunk_seconds: int) -> tuple[Path, list[tuple[float, Path]]]:
    """Split an mp3 into time-ordered chunks. Returns (tmpdir, [(offset_seconds, chunk_path)])."""
    tmpdir = Path(tempfile.mkdtemp(prefix="whisper_chunks_"))
    pattern = str(tmpdir / "chunk_%04d.mp3")
    subprocess.run(
        ["ffmpeg", "-i", str(audio_path), "-f", "segment", "-segment_time", str(chunk_seconds),
         "-c", "copy", "-y", pattern],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    chunks = sorted(tmpdir.glob("chunk_*.mp3"))
    return tmpdir, [(i * chunk_seconds, c) for i, c in enumerate(chunks)]


def _transcribe_audio_file(audio_file: Path) -> tuple[str, list[dict], str | None]:
    """One Whisper call. Returns (text, segments[{start,end,text}], language)."""
    with open(audio_file, "rb") as f:
        tr = _client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )
    segments = [
        {"start": round(s.start, 2), "end": round(s.end, 2), "text": (s.text or "").strip()}
        for s in (tr.segments or [])
    ]
    return tr.text.strip(), segments, getattr(tr, "language", None)


def _write_markdown(md_path: Path, payload: dict) -> None:
    """Human-readable companion: summary on top, then transcript with inline time markers."""
    lines = [f"# {Path(payload['filename']).stem}", ""]
    summary = payload.get("summary")
    if summary:
        lines.append("## Summary")
        if summary.get("abstract"):
            lines += [summary["abstract"], ""]
        for kp in summary.get("key_points", []):
            lines.append(f"- {kp}")
        lines.append("")
    lines.append("## Transcript")
    lines.append("")
    for hint in payload.get("timeline", []):
        lines.append(f"**[{hint['timestamp']}]** {hint['text']}")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def transcribe_video(
    path: str | Path,
    output_transcripts_dir: str | Path,
    *,
    interval_seconds: int = 60,
    summarize: bool = True,
) -> IngestedFile:
    path = Path(path)
    output_transcripts_dir = Path(output_transcripts_dir)
    output_transcripts_dir.mkdir(parents=True, exist_ok=True)

    file_type = "audio" if path.suffix.lower() in AUDIO_ONLY else "video"

    # Always extract a normalized small audio track (controls size, unifies handling).
    audio_path = _extract_audio(path)
    tmpdir = None
    try:
        if audio_path.stat().st_size <= WHISPER_LIMIT:
            chunks = [(0.0, audio_path)]
        else:
            tmpdir, chunks = _split_audio(audio_path, CHUNK_SECONDS)

        text_parts: list[str] = []
        segments: list[dict] = []
        language: str | None = None
        for offset, chunk_path in chunks:
            text, segs, lang = _transcribe_audio_file(chunk_path)
            language = language or lang
            if text:
                text_parts.append(text)
            for s in segs:
                segments.append(
                    {"start": round(s["start"] + offset, 2),
                     "end": round(s["end"] + offset, 2),
                     "text": s["text"]}
                )
    finally:
        if audio_path.exists():
            audio_path.unlink()
        if tmpdir is not None:
            for c in tmpdir.glob("*"):
                c.unlink()
            tmpdir.rmdir()

    transcript_text = " ".join(text_parts).strip()
    timeline = build_timeline(segments, interval_seconds=interval_seconds)
    duration = segments[-1]["end"] if segments else 0.0

    summary = summarize_transcript(transcript_text, title=path.stem) if summarize else None

    metadata = {
        "source_path": str(path),
        "duration_seconds": duration,
        "duration_hms": format_timestamp(duration),
    }
    if language:
        metadata["language"] = language

    payload = {
        "filename": path.name,
        "file_type": file_type,
        "content": transcript_text,
        "segments": segments,
        "timeline": timeline,
        "summary": summary,
        "metadata": metadata,
    }
    (output_transcripts_dir / f"{path.stem}_transcript.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _write_markdown(output_transcripts_dir / f"{path.stem}_transcript.md", payload)

    return IngestedFile(
        filename=path.name,
        file_type=file_type,
        content=transcript_text,
        segments=segments,
        timeline=timeline,
        summary=summary,
        metadata=metadata,
    )
