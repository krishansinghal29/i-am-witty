"""Sample every exercise generator N times and write an expandable markdown report.

For each registered exercise this calls the REAL generator LLM (no DB, no TTS) —
system prompt + the generator's seed (spark / verb / archetype) + structured
output — so we can eyeball variety and quality. Each generation is independent,
mirroring the runtime path in VoicePromptTaskEngine.generate.

Run:
    uv run python scripts/sample_generators.py
    uv run python scripts/sample_generators.py --runs 10 --concurrency 30
    uv run python scripts/sample_generators.py --exercises vibing,pushPull --no-seeds
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import re
import sys
import time
from pathlib import Path

# Ensure the backend root (parent of scripts/) is importable when run as a file.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.settings import get_settings  # noqa: E402
from app.infrastructure.runtime.prompts.registry import (  # noqa: E402
    get_exercise_spec,
    get_supported_exercise_keys,
)
from app.infrastructure.db.reference_data.task_catalog import TASKS  # noqa: E402

DEFAULT_OUT = "/Users/krishansinghal/i-am-witty/design/extra/generator_samples.md"
GENERATION_TEMPERATURE = 1.0  # matches VoicePromptTaskEngine._GENERATION_TEMPERATURE

_TITLE_BY_KEY = {t["runtime_config"]["backend_key"]: t["title"] for t in TASKS}

# Strip the two fixed boilerplate notes from a seed so only the varying part shows.
_SPARK_RE = re.compile(
    r"\s*For fresh inspiration only, here (?:is a random spark word|are random spark words): "
    r"(?P<sp>.*?)\. Let whatever.*$",
    re.S,
)
_SIMPLER_RE = re.compile(
    r"\s*If the seed word is uncommon.*?easy to understand\.", re.S
)


def _compact_seed(seed: str) -> str:
    s = _SIMPLER_RE.sub("", seed)
    m = _SPARK_RE.search(s)
    if m:
        s = s[: m.start()].rstrip() + f"  ·  spark: {m.group('sp')}"
    return " ".join(s.split())


def _md_escape(text: str) -> str:
    """Minimal escaping so generated text can't break the HTML <details> block."""
    return " ".join(text.split()).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_messages(messages: list[dict]) -> str:
    """One line for single-message specs; role-labelled for dialogue specs."""
    parts = [(m.get("role", ""), m.get("content", "")) for m in messages if m.get("content")]
    if not parts:
        return "(empty)"
    if len(parts) == 1:
        return parts[0][1]
    return " / ".join(f"{role}: {content}" for role, content in parts)


async def _generate_once(llm, spec, model, sem, *, show_seeds: bool) -> dict:
    seed = spec.generator_prompt()
    async with sem:
        try:
            result = await llm.complete_structured(
                messages=[
                    {"role": "system", "content": spec.generator_system},
                    {"role": "user", "content": seed},
                ],
                response_model=spec.generator_response_schema,
                temperature=GENERATION_TEMPERATURE,
                model=model,
            )
            text = _render_messages(result.model_dump()["messages"])
            return {"ok": True, "text": text, "seed": seed if show_seeds else None}
        except Exception as exc:  # noqa: BLE001 - report, never crash the batch
            return {"ok": False, "text": f"error: {exc!r}", "seed": seed if show_seeds else None}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", type=int, default=10, help="generations per exercise (default 10)")
    p.add_argument("--concurrency", type=int, default=30, help="max concurrent LLM calls (default 30)")
    p.add_argument("--out", default=DEFAULT_OUT, help="output markdown path")
    p.add_argument("--exercises", default="", help="comma-separated keys to limit to (default all)")
    p.add_argument("--no-seeds", dest="show_seeds", action="store_false", help="hide the seed under each line")
    p.set_defaults(show_seeds=True)
    return p.parse_args()


def _render_markdown(args, model, results: dict[str, list[dict]], elapsed: float) -> str:
    now = dt.datetime.now().isoformat(timespec="seconds")
    lines: list[str] = [
        f"# Generator samples — {args.runs} runs each",
        "",
        f"_model: `{model}` · temp {GENERATION_TEMPERATURE} · concurrency {args.concurrency} · "
        f"{len(results)} exercises · {now} · {elapsed:.1f}s_",
        "",
        "| exercise | title | unique | errors |",
        "| --- | --- | --- | --- |",
    ]
    for key, runs in results.items():
        ok = [r for r in runs if r["ok"]]
        unique = len({r["text"] for r in ok})
        errors = len(runs) - len(ok)
        lines.append(f"| `{key}` | {_TITLE_BY_KEY.get(key, '—')} | {unique}/{len(runs)} | {errors} |")
    lines.append("")

    for key, runs in results.items():
        ok = [r for r in runs if r["ok"]]
        unique = len({r["text"] for r in ok})
        title = _TITLE_BY_KEY.get(key, key)
        lines.append("<details>")
        lines.append(f"<summary><b>{key}</b> — {title} · unique {unique}/{len(runs)}</summary>")
        lines.append("")
        for i, r in enumerate(runs, 1):
            mark = "" if r["ok"] else "⚠️ "
            lines.append(f"{i}. {mark}{_md_escape(r['text'])}")
            if r.get("seed"):
                lines.append(f"   <sub>↳ seed: {_md_escape(_compact_seed(r['seed']))}</sub>")
        lines.append("")
        lines.append("</details>")
        lines.append("")
    return "\n".join(lines)


async def main() -> None:
    args = _parse_args()
    settings = get_settings()
    model = settings.llm_generator_model

    from app.infrastructure.integrations.litellm_provider import LiteLlmProvider

    llm = LiteLlmProvider(settings, default_model=model)

    keys = sorted(get_supported_exercise_keys())
    if args.exercises:
        wanted = {k.strip() for k in args.exercises.split(",") if k.strip()}
        keys = [k for k in keys if k in wanted]
        missing = wanted - set(keys)
        if missing:
            print(f"warning: unknown exercise keys ignored: {sorted(missing)}", file=sys.stderr)

    print(
        f"generating {args.runs}x for {len(keys)} exercises "
        f"({len(keys) * args.runs} calls) on {model}, concurrency {args.concurrency}...",
        file=sys.stderr,
    )

    sem = asyncio.Semaphore(args.concurrency)
    scheduled = {
        key: [
            asyncio.create_task(
                _generate_once(llm, get_exercise_spec(key), model, sem, show_seeds=args.show_seeds)
            )
            for _ in range(args.runs)
        ]
        for key in keys
    }

    t0 = time.perf_counter()
    results: dict[str, list[dict]] = {}
    for key, coros in scheduled.items():
        results[key] = await asyncio.gather(*coros)
        ok = sum(1 for r in results[key] if r["ok"])
        print(f"  {key:30s} {ok}/{len(coros)} ok", file=sys.stderr)
    elapsed = time.perf_counter() - t0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render_markdown(args, model, results, elapsed))
    print(f"\nwrote {out} ({elapsed:.1f}s)", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
