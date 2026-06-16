"""Smoke-test the rewritten First Unusual Thing evaluator on a few answers.

    PYTHONPATH=. .venv/bin/python ../extra/eval_smoke.py
"""
from __future__ import annotations

import asyncio
import re

from app.infrastructure.integrations.litellm_provider import LiteLlmProvider
from app.infrastructure.runtime.prompts.first_unusual_thing import SPEC
from app.settings import Settings

SCENE = "She lines up the sugar packets by color before she'll order."
CASES = [
    ("flat reaction", "Haha that's so particular."),
    ("label-only", "You must run a very tidy sugar cartel."),
    ("label + crazy exaggerate",
     "You're clearly a condiment quality inspector — by date three you'll be auditing my spice rack and writing me up."),
]

provider = LiteLlmProvider(Settings())


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


async def run(label: str, answer: str) -> None:
    prompt = SPEC.evaluator_prompt(
        question_data=[{"role": "She", "content": SCENE}],
        transcription=answer,
        technique_name=None,
    )
    res = await provider.complete_structured(
        messages=[
            {"role": "system", "content": SPEC.evaluator_system},
            {"role": "user", "content": prompt},
        ],
        response_model=SPEC.evaluator_response_schema,
        temperature=1.0,
    )
    data = res.model_dump()
    print(f"\n{'='*70}\nCASE: {label}\nANSWER: {answer}\n{'-'*70}")
    print("FEEDBACK:\n" + strip_html(data["feedback"]))
    print("\nSAMPLE:\n" + strip_html(data["sample_answer"]))


async def main() -> None:
    await asyncio.gather(*[run(lbl, ans) for lbl, ans in CASES])


if __name__ == "__main__":
    asyncio.run(main())
