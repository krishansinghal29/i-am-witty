from __future__ import annotations
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
from pathlib import Path
from models import IngestedFile
from modules.ingestion.text_parser import parse_text_file
from modules.ingestion.video_transcriber import transcribe_video

TEXT_EXTS = {".txt", ".md", ".html", ".htm"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a"}


SKIP_NAMES = {".ds_store", "thumbs.db"}
SKIP_EXTS = {".json"}


def ingest_directory(input_dir: str | Path, output_dir: str | Path) -> list[IngestedFile]:
    input_dir = Path(input_dir)
    results: list[IngestedFile] = []

    for path in input_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.name.lower() in SKIP_NAMES:
            continue
        if path.suffix.lower() in SKIP_EXTS:
            continue

        suffix = path.suffix.lower()
        json_path = path.with_name(f"{path.stem}_transcript.json")

        if json_path.exists():
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            print(f"   Cached: {path.name}")
            results.append(IngestedFile(**data))
            continue

        if suffix in TEXT_EXTS:
            ingested = parse_text_file(path)
            out = {
                "filename": ingested.filename,
                "file_type": ingested.file_type,
                "content": ingested.content,
                "metadata": ingested.metadata,
            }
            json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
            results.append(ingested)
        elif suffix in VIDEO_EXTS | AUDIO_EXTS:
            ingested = transcribe_video(path, path.parent)
            results.append(ingested)
        else:
            print(f"   Warning: skipping unsupported file '{path.name}'")

    return results
