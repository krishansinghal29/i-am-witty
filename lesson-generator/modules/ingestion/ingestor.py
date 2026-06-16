from __future__ import annotations
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from models import IngestedFile
from modules.ingestion.text_parser import parse_text_file
from modules.ingestion.video_transcriber import transcribe_video

TEXT_EXTS = {".txt", ".md", ".html", ".htm"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a"}


SKIP_NAMES = {".ds_store", "thumbs.db"}
SKIP_EXTS = {".json"}

_print_lock = threading.Lock()


def _log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def _process_file(
    path: Path,
    *,
    force: bool,
    interval_seconds: int,
    summarize: bool,
) -> tuple[str, Path, object]:
    """Process a single file. Returns (status, path, result_or_error). Never raises."""
    suffix = path.suffix.lower()
    json_path = path.with_name(f"{path.stem}_transcript.json")

    if json_path.exists() and not force:
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            return ("cached", path, IngestedFile.from_dict(data))
        except Exception:
            pass  # corrupt cache -> regenerate below

    try:
        if suffix in TEXT_EXTS:
            ingested = parse_text_file(path)
            out = {
                "filename": ingested.filename,
                "file_type": ingested.file_type,
                "content": ingested.content,
                "metadata": ingested.metadata,
            }
            json_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
            return ("text", path, ingested)
        elif suffix in VIDEO_EXTS | AUDIO_EXTS:
            ingested = transcribe_video(
                path, path.parent,
                interval_seconds=interval_seconds,
                summarize=summarize,
            )
            return ("media", path, ingested)
        else:
            return ("skip", path, None)
    except Exception as e:
        return ("error", path, e)


def ingest_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    force: bool = False,
    interval_seconds: int = 60,
    summarize: bool = True,
    concurrency: int = 16,
) -> list[IngestedFile]:
    input_dir = Path(input_dir)
    results: list[IngestedFile] = []
    errors: list[tuple[str, str]] = []

    media_paths = [
        p for p in sorted(input_dir.rglob("*"))
        if p.is_file()
        and p.name.lower() not in SKIP_NAMES
        and p.suffix.lower() not in SKIP_EXTS
        and not p.name.endswith("_transcript.md")
    ]
    total = len(media_paths)
    _log(f"   {total} candidate file(s); concurrency={concurrency}")

    done = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {
            pool.submit(
                _process_file, p,
                force=force, interval_seconds=interval_seconds, summarize=summarize,
            ): p
            for p in media_paths
        }
        for fut in as_completed(futures):
            done += 1
            status, path, result = fut.result()
            prefix = f"   [{done}/{total}]"
            if status == "cached":
                results.append(result)
                _log(f"{prefix} Cached: {path.name}")
            elif status == "text":
                results.append(result)
                _log(f"{prefix} Parsed text: {path.name}")
            elif status == "media":
                results.append(result)
                _log(f"{prefix} Done: {path.name} "
                     f"({result.metadata.get('duration_hms', '?')}, {len(result.timeline)} hints)")
            elif status == "skip":
                _log(f"{prefix} Skipping unsupported: {path.name}")
            else:  # error
                errors.append((str(path), str(result)))
                _log(f"{prefix} ERROR on {path.name}: {result}")

    if errors:
        _log(f"\n   Completed with {len(errors)} error(s):")
        for p, e in errors:
            _log(f"     - {p}: {e}")

    return results
