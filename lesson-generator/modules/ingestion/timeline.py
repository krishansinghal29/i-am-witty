"""Build interval-based timeline hints from timestamped transcript segments."""
from __future__ import annotations


def format_timestamp(seconds: float) -> str:
    """Seconds -> 'MM:SS' (or 'HH:MM:SS' past the hour)."""
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def build_timeline(segments: list[dict], interval_seconds: int = 60) -> list[dict]:
    """Group segment text into fixed-width time buckets.

    Each returned hint marks where, in the audio timeline, a chunk of transcript
    sits: {"timestamp": "MM:SS", "start_seconds": int, "text": "..."}.
    With the default 60s interval this yields one hint per minute.
    """
    if not segments:
        return []

    buckets: dict[int, list[str]] = {}
    for seg in segments:
        idx = int(seg["start"] // interval_seconds)
        text = (seg.get("text") or "").strip()
        if text:
            buckets.setdefault(idx, []).append(text)

    timeline = []
    for idx in sorted(buckets):
        start = idx * interval_seconds
        timeline.append(
            {
                "timestamp": format_timestamp(start),
                "start_seconds": start,
                "text": " ".join(buckets[idx]).strip(),
            }
        )
    return timeline
