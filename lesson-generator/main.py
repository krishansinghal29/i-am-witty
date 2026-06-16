from __future__ import annotations
import json
import click
from pathlib import Path

from modules.ingestion.ingestor import ingest_directory
from modules.script_generator.generator import generate_script
from modules.audio_generator.generator import generate_audio


@click.command()
@click.option("--input", "input_dir", required=True, type=click.Path(exists=True), help="Directory containing source content files")
@click.option("--output", "output_dir", default="./output", type=click.Path(), help="Directory for generated outputs")
@click.option("--voice", "voice_id", default=None, help="ElevenLabs voice ID (overrides .env)")
@click.option("--module", "module", default="all", type=click.Choice(["1", "2", "3", "all"]), help="Run a specific module or the full pipeline")
@click.option("--topic", "topic", default=None, help="Lesson topic — filters source material to relevant content (required for module 2)")
@click.option("--force", is_flag=True, default=False, help="Module 1: re-transcribe even if a cached _transcript.json exists")
@click.option("--interval", "interval", default=60, type=int, help="Module 1: timeline hint interval in seconds (default 60)")
@click.option("--no-summary", "no_summary", is_flag=True, default=False, help="Module 1: skip per-video summary generation")
@click.option("--concurrency", "concurrency", default=16, type=int, help="Module 1: number of files to process in parallel (default 16)")
def main(input_dir: str, output_dir: str, voice_id: str | None, module: str, topic: str | None,
         force: bool, interval: int, no_summary: bool, concurrency: int):
    """Lesson Generator — converts mixed content into a spoken audio lesson."""
    output_path = Path(output_dir)
    (output_path / "scripts").mkdir(parents=True, exist_ok=True)
    (output_path / "audio").mkdir(parents=True, exist_ok=True)

    ingested = None
    script = None

    if module in ("1", "all"):
        click.echo("── Module 1: Ingesting content (transcript + timeline + summary)...")
        ingested = ingest_directory(
            input_dir, output_dir,
            force=force, interval_seconds=interval, summarize=not no_summary,
            concurrency=concurrency,
        )
        click.echo(f"   Ingested {len(ingested)} file(s).")

    if module in ("2", "all"):
        if not topic:
            raise click.UsageError("--topic is required for module 2. Example: --topic \"how to close an interaction\"")
        topic_slug = topic.lower().replace(" ", "_")[:60]
        script_json = output_path / "scripts" / f"lesson_script_{topic_slug}.json"
        if script_json.exists():
            click.echo(f"── Module 2: Cached — loading existing script for topic '{topic}'.")
            script = _load_script(script_json)
        else:
            if ingested is None:
                ingested = _load_ingested(Path(input_dir))
            click.echo(f"── Module 2: Generating lesson script for topic '{topic}'...")
            script = generate_script(ingested, topic)
            _save_script(script, output_path / "scripts", topic_slug)
            click.echo(f"   Script saved: {script.title} (~{script.estimated_duration_secs}s)")

    if module in ("3", "all"):
        if script is None:
            script, topic_slug = _resolve_script(output_path / "scripts", topic)
        else:
            topic_slug = (topic.lower().replace(" ", "_")[:60]) if topic else "default"
        audio_path = output_path / "audio" / f"lesson_{topic_slug}.mp3"
        if audio_path.exists() and audio_path.stat().st_size > 0:
            click.echo(f"── Module 3: Cached — {audio_path} already exists.")
        else:
            click.echo("── Module 3: Generating audio...")
            audio = generate_audio(script, output_path / "audio", voice_id=voice_id, filename=f"lesson_{topic_slug}.mp3")
            click.echo(f"   Audio saved: {audio.file_path}")

    click.echo("Done.")


def _save_script(script, scripts_dir: Path, topic_slug: str = "default"):
    from dataclasses import asdict
    with open(scripts_dir / f"lesson_script_{topic_slug}.json", "w") as f:
        json.dump(asdict(script), f, indent=2)
    with open(scripts_dir / f"lesson_script_{topic_slug}.txt", "w") as f:
        f.write(script.raw_text)


def _resolve_script(scripts_dir: Path, topic: str | None):
    """Load the right script file. Uses --topic if given; auto-detects if only one exists."""
    if topic:
        slug = topic.lower().replace(" ", "_")[:60]
        return _load_script(scripts_dir / f"lesson_script_{slug}.json"), slug

    candidates = list(scripts_dir.glob("lesson_script_*.json"))
    if len(candidates) == 1:
        slug = candidates[0].stem.removeprefix("lesson_script_")
        return _load_script(candidates[0]), slug
    if len(candidates) == 0:
        raise click.UsageError("No script found in output/scripts/. Run module 2 first.")
    slugs = [c.stem.removeprefix("lesson_script_") for c in candidates]
    raise click.UsageError(
        f"Multiple scripts found — specify one with --topic:\n  " + "\n  ".join(slugs)
    )


def _load_script(path: Path):
    import json
    from models import LessonScript, ScriptSegment
    with open(path) as f:
        data = json.load(f)
    data["segments"] = [ScriptSegment(**s) for s in data["segments"]]
    return LessonScript(**data)


def _load_ingested(input_dir: Path):
    from models import IngestedFile
    files = []
    for p in input_dir.rglob("*.json"):
        with open(p) as f:
            data = json.load(f)
        files.append(IngestedFile.from_dict(data))
    return files


if __name__ == "__main__":
    main()
