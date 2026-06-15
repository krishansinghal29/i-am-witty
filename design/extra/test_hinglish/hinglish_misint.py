"""Standalone Hinglish MISINTERPRETATION test harness (self-contained).

Mirrors the real misinterpretation runtime path:
  1. Generator -> produces N ordinary romanized-Hinglish sentences containing a
     pronoun (main / tu / tum / hum), the kind a real person actually says.
  2. Evaluator -> runs on an EMPTY user response for each sentence, so we see the
     sentence quality AND the evaluator's own Hinglish sample misinterpretations.

Output: results_misint.md in this folder.

Run (from this folder):
    ../../backend/.venv/bin/python hinglish_misint.py
    ../../backend/.venv/bin/python hinglish_misint.py --runs 25 \
        --gen-model gemini/gemini-2.5-flash --eval-model gemini/gemini-2.5-pro
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import os
import random
import sys
import time
from pathlib import Path

from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
BACKEND_ENV = HERE.parent.parent / "backend" / ".env"
DEFAULT_OUT = HERE / "results_misint.md"

GENERATION_TEMPERATURE = 1.0
EVALUATION_TEMPERATURE = 0.3


def load_keys() -> None:
    if not BACKEND_ENV.exists():
        return
    for line in BACKEND_ENV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key in ("GEMINI_API_KEY", "OPENAI_API_KEY") and value and key not in os.environ:
            os.environ[key] = value


class Sentence(BaseModel):
    sentence: str = Field(..., min_length=1, description="One ordinary romanized-Hinglish sentence with main/tu/tum/hum.")


class Evaluation(BaseModel):
    feedback: str = Field(..., min_length=1, description="Romanized-Hinglish feedback, 4-section structure.")
    sample_answer: str = Field(..., min_length=1, description="3 romanized-Hinglish misinterpretations, separated by <br><br>.")


# --------------------------------------------------------------------------- #
# Generator                                                                    #
# --------------------------------------------------------------------------- #
GENERATOR_SYSTEM = """You generate ordinary, everyday sentences for a MISINTERPRETATION exercise, written in natural ROMANIZED HINGLISH — Hindi-English code-mixing the way urban Indians actually text and speak. Latin script only, never Devanagari.

You receive a seed: a verb (inspiration only) and a pronoun (main / tu / tum / hum). Write ONE short, completely ordinary sentence that a real person would actually say in everyday life — to a friend, partner, colleague.

The sentence must:
- Use the given pronoun (main / tu / tum / hum) naturally.
- Be inspired by the verb (don't quote it; pick a natural everyday form of the action).
- Sound 100% NORMAL — NOT clever, NOT a joke, NOT already a double-meaning. The wit comes later when someone misreads it; your job is to write the plain, innocent line.
- Have everyday texture a listener could later twist (a word, a modifier, an ambiguity) — but you do NOT engineer the twist, you just write the natural sentence.

Register rules:
- Natural spoken code-mix of a 20-something in a Tier-1 Indian city. NOT translated/textbook Hindi, NOT pure English.
- Keep words Indians keep in English in English (phone, plan, office, traffic, charge, light, message).
- Casual, like a real WhatsApp/voice-note line.

Output rules:
- EXACTLY ONE sentence. Romanized Hinglish. No Devanagari. No quotation marks. No emojis. No preamble. Output only the sentence."""

GENERATOR_FEWSHOT = """Examples of the plain, ordinary register (do NOT copy, just match the feel):
- Main aaj raat ko jaldi nikal jaunga office se.
- Tu hamesha mujhe last minute pe batati hai.
- Hum kal milte hain phir detail mein baat karenge.
- Tum thodi der ke liye phone pakad lo na."""

GENERATOR_ASK = "Generate one new ordinary Hinglish sentence now, strictly following the system instructions."

PRONOUNS = ["main", "tu", "tum", "hum"]
SPARK_VERBS = [
    "wait", "charge", "drop", "hold", "catch", "miss", "follow", "leave", "run",
    "pick", "lose", "carry", "watch", "save", "push", "pull", "check", "fix",
    "break", "turn", "block", "share", "cut", "hit", "pass", "book", "cancel",
    "settle", "handle", "cover", "spot", "land", "trip", "stretch",
]


def build_seed() -> str:
    verb = random.choice(SPARK_VERBS)
    pronoun = random.choice(PRONOUNS)
    return f'{GENERATOR_ASK}\n\nSeed verb (inspiration): "{verb}". Pronoun to use: "{pronoun}".'


# --------------------------------------------------------------------------- #
# Evaluator (Hinglish feedback + Hinglish sample misinterpretations)           #
# --------------------------------------------------------------------------- #
EVALUATOR_SYSTEM = """You are a wit coach evaluating "Misinterpretation" responses for an Indian audience. The skill: take an ordinary sentence and respond as if you understood it differently — find an alternative reading and run with it confidently. You are NOT correcting them; you are living in the wrong meaning on purpose.

=== EVALUATION CONTEXT ===
You only have a transcript of the user's spoken response (romanized Hinglish, possibly imperfect). Judge CONTENT and intent, not spelling, audio, or delivery. The transcript may be EMPTY — if so, treat it as "no attempt", say so kindly in the feedback, and still produce three strong sample misinterpretations so the learner sees what good looks like.

=== WHAT COUNTS AS MISINTERPRETATION ===
The humour must come from MISREADING something in the original sentence itself — a word, a modifier, a pronoun, an ambiguity, a phrase. Not from reacting to it.
LITMUS TEST: if the response still makes sense under the sentence's intended meaning, it is NOT a misinterpretation — fail it.
A response is NOT a misinterpretation if it just agrees, reacts emotionally, continues the topic normally, or escalates enthusiasm about the real subject.

=== MISINTERPRETATION TECHNIQUES (Hinglish) ===
1. Literal Trap (figurative ko literal le lo): "Main aaj mar jaunga kaam se" -> "Arre toh arrangements main karu ya tu khud dekh lega?"
2. Context Shift (alag situation maan lo): "Hum yahin ruk jaate hain" -> "Itni jaldi? Abhi toh ek hafta hi hua hai humein mile."
3. Scope Explosion (chhoti baat ko huge bana do): "Tere saamne main hamesha keys kho deta hoon" -> "Matlab main hoon hi nahi, teri presence meri puri life rearrange kar deti hai."
4. Innuendo (innocent line mein subtext): "Tu itna time kyun leti hai" -> "Suna hai har second worth it hota hai."
5. Absurd Escalation (ridiculous conclusion tak le jao): "Main tere saath keep up nahi kar pata" -> "Koi nahi kar pata, scientists research kar rahe hain ispe."
6. Subject Flip ("tu/hum" ka reference ghuma do): "Tu hamesha aisa karta hai" -> "Kya karta hoon — bhulaaye na bhulu, yeh? Haan woh meri galti hai."

=== EVALUATION CRITERIA ===
1. Litmus test first: kya response original sentence ke seedhe matlab mein bhi sahi baithta hai? Agar haan, toh yeh misinterpretation nahi — fail.
2. Kya misread hua: woh specific word/modifier/pronoun/phrase identify karo jo galat parse hua. Naam na le pao toh misinterpretation hua hi nahi.
3. Fit: misreading sentence ki kisi cheez se plausibly connect kare — random na ho.
4. Wit: misreading clever, surprising ya funny ho.
5. Brevity: 1-2 sentences max.

=== FEEDBACK FORMAT (FOLLOW EXACTLY) ===
Write ALL feedback in natural romanized Hinglish. No emojis. Use this 4-section HTML structure:

<b>✅ Kya Landed</b><br>
Kya kaam kiya. Possible ho toh unke words quote karo. 1-2 sentences max.
<br><br>
<b>⚠️ Trap</b><br>
Specific mistake (common traps: CONTINUATION = sentence ko naturally continue kiya, kuch misread nahi — litmus fail; FORCED = misreading sentence se connect hi nahi karti; BROKE THE BIT = "haha mazaak kar raha tha" ya joke explain kiya; TOO LONG = 3 sentence ki speech; RANDOM = sentence se koi lena-dena nahi). 1-2 sentences max.
<br><br>
<b>🚀 Level Up</b><br>
Upar di gayi ek technique se ek concrete suggestion. 1-2 sentences max.
<br><br>
<b>🧠 Mindset Shift</b><br>
Ek root-cause reframe (e.g. "Har sentence ka ek surface meaning hota hai aur ek aur — tumhara kaam us doosre meaning mein jaake confidently reh jaana hai."). 1-2 sentences max.

=== SAMPLE ANSWER GUIDELINES ===
Generate exactly 3 sample misinterpretations of the given sentence, in romanized Hinglish, separated by <br><br>. Each must use a DIFFERENT technique from the list above, be SHORT (1-2 sentences), commit fully to the wrong reading (no hedging, no explaining), and clearly misread something specific in the sentence. No emojis.

=== OUTPUT CONTRACT ===
Return exactly two fields:
- feedback: the 4-section HTML above (Hinglish).
- sample_answer: exactly 3 misinterpretations separated by <br><br> (Hinglish)."""


def evaluator_user_prompt(sentence: str, transcript: str) -> str:
    return (
        "**Exercise Type:** misinterpretationHinglish\n"
        "**Tease/Statement:** " + sentence + "\n"
        "**User's Response Transcript:** " + (transcript.strip() if transcript.strip() else "(empty — no response)")
    )


# --------------------------------------------------------------------------- #
# LLM calls                                                                     #
# --------------------------------------------------------------------------- #
async def generate_one(model: str, sem: asyncio.Semaphore) -> dict:
    import litellm

    seed = build_seed()
    async with sem:
        try:
            resp = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": GENERATOR_SYSTEM + "\n\n" + GENERATOR_FEWSHOT},
                    {"role": "user", "content": seed},
                ],
                response_format=Sentence,
                temperature=GENERATION_TEMPERATURE,
                max_tokens=2000,
                num_retries=2,
            )
            text = Sentence.model_validate_json(resp.choices[0].message.content).sentence.strip()
            return {"ok": True, "sentence": text, "seed": seed}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "sentence": f"ERROR: {exc!r}", "seed": seed}


async def evaluate_one(model: str, sentence: str, sem: asyncio.Semaphore) -> dict:
    import litellm

    async with sem:
        try:
            resp = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": EVALUATOR_SYSTEM},
                    {"role": "user", "content": evaluator_user_prompt(sentence, "")},
                ],
                response_format=Evaluation,
                temperature=EVALUATION_TEMPERATURE,
                max_tokens=3000,
                num_retries=2,
            )
            data = Evaluation.model_validate_json(resp.choices[0].message.content)
            return {"ok": True, "feedback": data.feedback, "sample_answer": data.sample_answer}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "feedback": f"ERROR: {exc!r}", "sample_answer": ""}


def render_md(args, gens: list[dict], evals: list[dict], elapsed: float) -> str:
    now = dt.datetime.now().isoformat(timespec="seconds")
    ok_gen = [g for g in gens if g["ok"]]
    unique = len({g["sentence"] for g in ok_gen})
    lines = [
        "# Hinglish misinterpretation — generator + evaluator(empty response) test",
        "",
        f"_gen: `{args.gen_model}` (temp {GENERATION_TEMPERATURE}) · "
        f"eval: `{args.eval_model}` (temp {EVALUATION_TEMPERATURE}) · "
        f"{len(gens)} sentences · unique {unique}/{len(ok_gen)} · {now} · {elapsed:.1f}s_",
        "",
        "Romanized Hinglish · feedback language Hinglish · evaluator run on EMPTY user responses.",
        "The evaluator's sample answers are the thing to eyeball: are they real misinterpretations (misread a word), in natural Hinglish?",
        "",
        "---",
        "",
    ]
    for i, (g, e) in enumerate(zip(gens, evals), 1):
        mark = "" if g["ok"] else "⚠️ "
        lines.append(f"### {i}. {mark}{g['sentence']}")
        lines.append("")
        if e["ok"]:
            lines.append("<details><summary>evaluator output (empty response)</summary>")
            lines.append("")
            lines.append("**Feedback:**")
            lines.append("")
            lines.append(e["feedback"])
            lines.append("")
            lines.append("**Sample misinterpretations:**")
            lines.append("")
            lines.append(e["sample_answer"])
            lines.append("")
            lines.append("</details>")
        else:
            lines.append(f"⚠️ eval error: {e['feedback']}")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", type=int, default=22)
    p.add_argument("--concurrency", type=int, default=6)
    p.add_argument("--gen-model", default="gpt-5.3-chat-latest")
    p.add_argument("--eval-model", default="gpt-5.3-chat-latest")
    p.add_argument("--out", default=str(DEFAULT_OUT))
    return p.parse_args()


async def main() -> None:
    args = parse_args()
    load_keys()
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        sys.exit("No GEMINI_API_KEY / OPENAI_API_KEY found (looked in backend/.env).")

    import litellm

    litellm.drop_params = True

    sem = asyncio.Semaphore(args.concurrency)
    t0 = time.perf_counter()

    print(f"generating {args.runs} sentences on {args.gen_model}...", file=sys.stderr)
    gens = await asyncio.gather(*[generate_one(args.gen_model, sem) for _ in range(args.runs)])
    print(f"  {sum(1 for g in gens if g['ok'])}/{len(gens)} generated", file=sys.stderr)

    print(f"evaluating empty responses on {args.eval_model}...", file=sys.stderr)
    evals = await asyncio.gather(*[evaluate_one(args.eval_model, g["sentence"], sem) for g in gens])
    print(f"  {sum(1 for e in evals if e['ok'])}/{len(evals)} evaluated", file=sys.stderr)

    elapsed = time.perf_counter() - t0
    Path(args.out).write_text(render_md(args, gens, evals, elapsed))
    print(f"\nwrote {args.out} ({elapsed:.1f}s)", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
