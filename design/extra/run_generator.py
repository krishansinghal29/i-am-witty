"""Run the First Unusual Thing generator 100x and dump the scenes.

Run from design/backend with the project venv so `app...` imports resolve and
`.env` (API keys + model) is picked up:

    .venv/bin/python ../extra/run_generator.py
"""
from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from pathlib import Path

from app.infrastructure.integrations.litellm_provider import LiteLlmProvider
from app.infrastructure.runtime.prompts.first_unusual_thing import SPEC
from app.settings import Settings

OUT_DIR = Path(__file__).resolve().parent
N = 100
CONCURRENCY = 10

settings = Settings()
provider = LiteLlmProvider(settings)


def parse_seed(seed: str) -> tuple[str, str]:
    """Drop the appended simpler-language note for display; pull the seed type."""
    core = seed.split(" If the seed word", 1)[0].strip()
    stype = core.split(".")[0].replace("Seed type: ", "").strip()
    return stype, core


async def one(i: int, sem: asyncio.Semaphore) -> dict:
    seed = SPEC.generator_prompt()
    stype, core = parse_seed(seed)
    async with sem:
        try:
            res = await provider.complete_structured(
                messages=[
                    {"role": "system", "content": SPEC.generator_system},
                    {"role": "user", "content": seed},
                ],
                response_model=SPEC.generator_response_schema,
                temperature=1.0,
            )
            return {"i": i, "type": stype, "seed": core,
                    "scene": res.messages[0].content.strip(), "error": None}
        except Exception as exc:  # noqa: BLE001 - record and continue
            return {"i": i, "type": stype, "seed": core,
                    "scene": None, "error": f"{type(exc).__name__}: {exc}"}


async def main() -> None:
    sem = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(*[one(i, sem) for i in range(N)])
    results.sort(key=lambda r: (r["type"], r["i"]))

    (OUT_DIR / "first_unusual_thing_scenarios.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n"
    )

    by: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by[r["type"]].append(r)
    ok = sum(1 for r in results if r["error"] is None)

    lines = [
        "# First Unusual Thing — 100 generated scenarios",
        "",
        f"Model: `{settings.llm_generator_model}` · temperature 1.0 · "
        f"{ok}/{len(results)} succeeded",
    ]
    for stype in sorted(by):
        lines.append(f"\n## {stype}  ({len(by[stype])})\n")
        for r in by[stype]:
            if r["error"]:
                lines.append(f"- ⚠️ `{r['seed']}` → ERROR: {r['error']}")
            else:
                lines.append(f"- **seed:** `{r['seed']}`\n  - {r['scene']}")
    (OUT_DIR / "first_unusual_thing_scenarios.md").write_text("\n".join(lines) + "\n")

    print(f"{ok}/{len(results)} succeeded")
    for r in results:
        if r["error"]:
            print("FAIL", r["type"], r["error"])


if __name__ == "__main__":
    asyncio.run(main())
