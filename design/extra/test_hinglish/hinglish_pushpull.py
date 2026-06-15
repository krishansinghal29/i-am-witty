"""Standalone Hinglish push-pull test harness (self-contained, no backend imports).

Mirrors the real runtime path conceptually:
  1. Generator  -> produces N romanized-Hinglish "She" scenarios (one per call).
  2. Evaluator  -> runs on an EMPTY user response for each scenario, so we see
     both the scenario quality AND the evaluator's own Hinglish sample answers /
     feedback structure in one pass.

Output: results.md (expandable report) in this folder.

Run (from this folder):
    ../../backend/.venv/bin/python hinglish_pushpull.py
    ../../backend/.venv/bin/python hinglish_pushpull.py --runs 25 \
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
DEFAULT_OUT = HERE / "results.md"

GENERATION_TEMPERATURE = 1.0
EVALUATION_TEMPERATURE = 0.3  # an evaluator wants consistency, not creativity


# --------------------------------------------------------------------------- #
# Keys: pull GEMINI_API_KEY / OPENAI_API_KEY out of the backend .env into env  #
# (litellm reads them from the environment). We only READ that file.            #
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Structured-output schemas                                                     #
# --------------------------------------------------------------------------- #
class Scenario(BaseModel):
    scenario: str = Field(..., min_length=1, description="One romanized-Hinglish sentence about her, role 'She'.")


class Evaluation(BaseModel):
    feedback: str = Field(..., min_length=1, description="Romanized-Hinglish feedback, 4-section structure.")
    sample_answer: str = Field(..., min_length=1, description="3 romanized-Hinglish push-pull responses, separated by <br><br>.")


# --------------------------------------------------------------------------- #
# Generator                                                                    #
# --------------------------------------------------------------------------- #
GENERATOR_SYSTEM = """You generate short, observable scenarios about a woman, written in natural ROMANIZED HINGLISH — Hindi-English code-mixing the way urban Indians actually text and speak. Latin script only, never Devanagari.

You receive a seed with a type and a value. Write ONE specific, concrete sentence describing something observable about her — a behaviour, a trait shown in a moment, or a physical/style detail — that feels real and particular to this one person.

How to use each seed type (the seed word is only inspiration — never quote it, never stay literal):
- verb: a habitual behaviour the verb evokes. "Woh hamesha..." — specific and observable.
- adjective: a personality trait the adjective evokes, SHOWN through one concrete moment (not "woh [adj] hai").
- vibe (subject + adjective): how her {subject} (voice / laugh / energy / humour / presence) comes across, coloured by the adjective.
- appearance (subject + adjective): something she's wearing or a physical detail (dress / jacket / hair / nails / bag / earrings), coloured by the adjective.

Register rules (this is the whole point — get the Hinglish right):
- Natural spoken code-mix of a 20-something in a Tier-1 Indian city. NOT translated/textbook Hindi, NOT pure English.
- Keep words that Indians keep in English in English (coffee, phone, table, vibe, playlist, hoodie, meeting). Don't force-translate them.
- It should sound like something a friend would actually say out loud, casually.
- Observable and concrete, not abstract or judgemental.

Output rules:
- EXACTLY ONE sentence. Romanized Hinglish. No Devanagari. No quotation marks. No emojis. No preamble. Output only the sentence."""

GENERATOR_FEWSHOT = """Examples of the register (do NOT copy these, just match the feel):
- Tum coffee order karne se pehle har baar barista se uska naam pooch leti ho.
- Woh aise dhang se eyebrow raise karti hai jaise andar hi andar sab judge kar rahi ho.
- Tumhari oversized denim jacket pe itne saare pin lage hain ki ek aur lagao toh woh bag ban jayegi.
- Woh apni har story ke beech mein "wait wait wait, important part aa raha hai" zaroor bolti hai."""

GENERATOR_ASK = "Generate one new Hinglish scenario now, strictly following the system instructions."

VIBE_SUBJECTS = ["voice", "laugh", "energy", "humour", "presence", "delivery", "opinions", "timing"]
APPEARANCE_SUBJECTS = ["dress", "jacket", "hair", "nails", "bag", "earrings", "shoes", "kurta", "sneakers", "scarf", "rings", "makeup"]

# English spark words — pure entropy, never surfaced. Keeps 20+ generations distinct.
SPARK_ADJECTIVES = [
    "feral", "regal", "chaotic", "meticulous", "dreamy", "sardonic", "luminous", "restless",
    "deadpan", "theatrical", "unbothered", "magnetic", "prickly", "whimsical", "ferocious",
    "serene", "mischievous", "brooding", "electric", "stubborn", "velvety", "jittery",
    "imperious", "playful", "nostalgic", "blunt", "radiant", "skeptical", "buoyant", "wry",
]
SPARK_VERBS = [
    "hoard", "narrate", "interrupt", "wander", "fidget", "rank", "negotiate", "rehearse",
    "doodle", "overshare", "correct", "collect", "improvise", "linger", "dramatize",
    "investigate", "tease", "annotate", "curate", "deflect", "memorize", "reorganize",
]


def build_seed() -> str:
    seed_type = random.choices(
        ["verb", "adjective", "vibe", "appearance"], weights=[1, 1, 1, 2], k=1
    )[0]
    if seed_type == "verb":
        line = f'Seed type: verb. Value: "{random.choice(SPARK_VERBS)}"'
    elif seed_type == "adjective":
        line = f'Seed type: adjective. Value: "{random.choice(SPARK_ADJECTIVES)}"'
    elif seed_type == "vibe":
        line = f'Seed type: vibe. Subject: "{random.choice(VIBE_SUBJECTS)}", Adjective: "{random.choice(SPARK_ADJECTIVES)}"'
    else:
        line = f'Seed type: appearance. Subject: "{random.choice(APPEARANCE_SUBJECTS)}", Adjective: "{random.choice(SPARK_ADJECTIVES)}"'
    return f"{GENERATOR_ASK}\n\n{line}"


# --------------------------------------------------------------------------- #
# Evaluator (Hinglish feedback + Hinglish samples)                             #
# --------------------------------------------------------------------------- #
EVALUATOR_SYSTEM = """You are a wit coach evaluating "Push-Pull" responses for an Indian audience. Push-pull is the balance between genuine interest (the PULL) and playful challenge (the PUSH) that creates memorable tension. The golden rule: the push teases something TRIVIAL and observable (never a real insecurity), and the pull must be GENUINE (not sarcastic, not hollow).

=== EVALUATION CONTEXT ===
You only have a transcript of the user's spoken response (romanized Hinglish, possibly imperfect). Judge CONTENT and intent, not spelling, audio, tone, or delivery. The user's transcript may be EMPTY — if so, treat it as "no attempt", say so kindly in the feedback, and still produce three strong sample answers so the learner sees what good looks like.

=== PUSH-PULL TECHNIQUES (Hinglish) ===
1. Compliment -> Tease: "Tum genuinely interesting ho... jo mere liye thodi problem hai kyun ki ab main distract ho gaya."
2. Tease -> Compliment: "Tum ek walking chaos ho... aur weirdly is room ki sabse interesting insaan bhi."
3. Feigned reluctance: "Main yeh bolne wala nahi tha, par tumhari woh judging-wali eyebrow actually cute hai."

=== EVALUATION CRITERIA ===
1. Both sides present (cover-half test): cover the pull — kya ek SPECIFIC tease bachta hai? cover the push — kya ek SPECIFIC compliment bachta hai (not generic "tum interesting ho")? An intensified compliment ("distractingly pyaari", "annoyingly perfect") is STILL all-pull.
2. Push is trivial: kuch observable aur silly ko tease kare, koi real insecurity ko nahi.
3. Push is about HER: ek habit/trait/detail ko tease kare. "Tum bored lag rahi ho mujhse" is an accusation about the dynamic, not a tease — that fails.
4. Pull is genuine: real lage, sarcastic ya hollow nahi.
5. Tension: push aur pull together ek interesting charge banaye.
6. Brevity: 1-2 sentences max.
7. Naturalness: natural bola-jaane-wala Hinglish lage — translated/formal Hindi ya pure English nahi.

=== FEEDBACK FORMAT (FOLLOW EXACTLY) ===
Write ALL feedback in natural romanized Hinglish. Use this 4-section HTML structure:

<b>✅ Kya Landed</b><br>
Kya kaam kiya. Possible ho toh unke words quote karo. 1-2 sentences max.
<br><br>
<b>⚠️ Trap</b><br>
Specific mistake (common traps: ALL PUSH = sirf tease, koi interest signal nahi; ALL PULL = sirf compliment, koi edge nahi; FAKE PUSH = compliment jo push ke kapde pehne hai; MEAN = playful se aage badhke actually hurtful; HOLLOW PULL = compliment jo kuch matlab nahi rakhta; GENERIC = kisi pe bhi fit ho jaye; TOO LONG = 2 se zyada sentences). 1-2 sentences max.
<br><br>
<b>🚀 Level Up</b><br>
Upar di gayi ek technique se ek concrete suggestion. 1-2 sentences max.
<br><br>
<b>🧠 Mindset Shift</b><br>
Ek root-cause reframe (e.g. "Push prove karta hai ki tum dhyaan de rahe ho, pull prove karta hai ki jo dikha woh pasand aaya — dono sach hone chahiye."). 1-2 sentences max.

=== SAMPLE ANSWER GUIDELINES ===
Generate exactly 3 sample answers in romanized Hinglish, separated by <br><br>:
- First: a strong push-pull using technique 1 (compliment -> tease).
- Second: a different approach using technique 2 (tease -> compliment).
- Third: another using technique 3 (feigned reluctance).
Har ek SHORT ho (1-2 sentences), aur har ek mein ek push AUR ek pull dono ho. Natural Hinglish.

=== OUTPUT CONTRACT ===
Return exactly two fields:
- feedback: the 4-section HTML above (Hinglish).
- sample_answer: exactly 3 responses separated by <br><br> (Hinglish)."""


def evaluator_user_prompt(scenario: str, transcript: str) -> str:
    return (
        "**Exercise Type:** pushPullHinglish\n"
        "**Scenario (She):** " + scenario + "\n"
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
                response_format=Scenario,
                temperature=GENERATION_TEMPERATURE,
                max_tokens=2000,
                num_retries=2,
            )
            text = Scenario.model_validate_json(resp.choices[0].message.content).scenario.strip()
            return {"ok": True, "scenario": text, "seed": seed}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "scenario": f"ERROR: {exc!r}", "seed": seed}


async def evaluate_one(model: str, scenario: str, sem: asyncio.Semaphore) -> dict:
    import litellm

    async with sem:
        try:
            resp = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": EVALUATOR_SYSTEM},
                    {"role": "user", "content": evaluator_user_prompt(scenario, "")},
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


# --------------------------------------------------------------------------- #
# Report                                                                        #
# --------------------------------------------------------------------------- #
def render_md(args, gens: list[dict], evals: list[dict], elapsed: float) -> str:
    now = dt.datetime.now().isoformat(timespec="seconds")
    ok_gen = [g for g in gens if g["ok"]]
    unique = len({g["scenario"] for g in ok_gen})
    lines = [
        "# Hinglish push-pull — generator + evaluator(empty response) test",
        "",
        f"_gen: `{args.gen_model}` (temp {GENERATION_TEMPERATURE}) · "
        f"eval: `{args.eval_model}` (temp {EVALUATION_TEMPERATURE}) · "
        f"{len(gens)} scenarios · unique {unique}/{len(ok_gen)} · {now} · {elapsed:.1f}s_",
        "",
        "Romanized Hinglish · feedback language Hinglish · evaluator run on EMPTY user responses.",
        "",
        "---",
        "",
    ]
    for i, (g, e) in enumerate(zip(gens, evals), 1):
        mark = "" if g["ok"] else "⚠️ "
        lines.append(f"### {i}. {mark}{g['scenario']}")
        lines.append("")
        if e["ok"]:
            lines.append("<details><summary>evaluator output (empty response)</summary>")
            lines.append("")
            lines.append("**Feedback:**")
            lines.append("")
            lines.append(e["feedback"])
            lines.append("")
            lines.append("**Sample answers:**")
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
    p.add_argument("--runs", type=int, default=22, help="number of scenarios to generate (default 22)")
    p.add_argument("--concurrency", type=int, default=6)
    p.add_argument("--gen-model", default="gemini/gemini-2.5-flash")
    p.add_argument("--eval-model", default="gemini/gemini-2.5-pro")
    p.add_argument("--out", default=str(DEFAULT_OUT))
    return p.parse_args()


async def main() -> None:
    args = parse_args()
    load_keys()
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        sys.exit("No GEMINI_API_KEY / OPENAI_API_KEY found (looked in backend/.env).")

    import litellm

    litellm.drop_params = True  # so temperature etc. don't 400 on picky models

    sem = asyncio.Semaphore(args.concurrency)
    t0 = time.perf_counter()

    print(f"generating {args.runs} scenarios on {args.gen_model}...", file=sys.stderr)
    gens = await asyncio.gather(*[generate_one(args.gen_model, sem) for _ in range(args.runs)])
    ok = sum(1 for g in gens if g["ok"])
    print(f"  {ok}/{len(gens)} generated", file=sys.stderr)

    print(f"evaluating empty responses on {args.eval_model}...", file=sys.stderr)
    evals = await asyncio.gather(*[evaluate_one(args.eval_model, g["scenario"], sem) for g in gens])
    ok_e = sum(1 for e in evals if e["ok"])
    print(f"  {ok_e}/{len(evals)} evaluated", file=sys.stderr)

    elapsed = time.perf_counter() - t0
    out = Path(args.out)
    out.write_text(render_md(args, gens, evals, elapsed))
    print(f"\nwrote {out} ({elapsed:.1f}s)", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
