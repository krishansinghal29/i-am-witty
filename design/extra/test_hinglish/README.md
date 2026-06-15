# Hinglish exercise experiment

Self-contained spike to test whether riffy's voice exercises work in **romanized Hinglish**
(Hindi-English code-mix in Latin script) — both the **generator** (produces the prompt the
user responds to) and the **evaluator** (scores the user's spoken answer and gives coaching
feedback). Two exercises were ported: **push-pull** and **misinterpretation**.

Everything here is isolated to this folder — no backend files were modified. The scripts are
standalone (they don't import the backend package); they only *read* `backend/.env` to pick up
API keys.

---

## Files

| File | What it is |
|---|---|
| `hinglish_pushpull.py` | Hinglish push-pull generator + evaluator harness |
| `results.md` | Push-pull output: 22 generated scenarios + evaluator output on empty responses |
| `hinglish_misint.py` | Hinglish misinterpretation generator + evaluator harness |
| `results_misint.md` | Misinterpretation output: 22 generated sentences + evaluator output on empty responses |
| `README.md` | This file |

## How to run

```bash
cd extra/test_hinglish
# push-pull (defaults: 22 runs, gpt-5.3-chat-latest for both)
../../backend/.venv/bin/python hinglish_pushpull.py
# misinterpretation
../../backend/.venv/bin/python hinglish_misint.py

# override models / count:
../../backend/.venv/bin/python hinglish_pushpull.py --runs 25 \
    --gen-model gemini/gemini-2.5-flash --eval-model gemini/gemini-2.5-flash
```

Each script: generates N prompts, then runs the evaluator on an **empty** user response for each
one. The empty-response trick is deliberate — it makes the evaluator emit its own *sample answers*
for every prompt, so a single pass lets you eyeball **both** generator quality (the prompts) and
evaluator quality (the model's own ideal Hinglish answers).

---

## Part 1 — Initial analysis & recommendations (the brainstorm)

### How the real exercises work (`backend/app/infrastructure/runtime/`)

- One `ExerciseSpec` per exercise (`prompts/push_pull.py`, `prompts/misinterpretation.py`),
  registered in `prompts/registry.py`, executed by `voice_prompt_engine.py`.
- **Generator**: `system` prompt + a randomized **seed** (a spark word from large English word
  lists — pure entropy, never surfaced) → one structured-output sentence. Temp 1.0.
  - push-pull → an observable scenario about a woman (role `"She"`).
  - misinterpretation → an ordinary everyday sentence containing `I`/`you`/`we`.
- **Evaluator**: `system` prompt (what-it-is, techniques, criteria, traps, sample-answer rules) +
  the user's **transcript** → `feedback` + `sample_answer` HTML. Temp 1.0.
- **Models** (`settings.py`): both default to `gpt-5.3-chat-latest`, routed via **litellm**
  (`litellm_provider.py`, `drop_params=True`), so any `anthropic/…` or `gemini/…` model string
  also works. Structured output via `response_format=PydanticModel`.

### The hidden dependency (deferred for now, per request)

The evaluator never hears audio — it scores a **Deepgram STT transcript**, and the generated
prompt is spoken by **OpenAI TTS ("nova")**. "Making the exercise Hinglish" is therefore *also*
an STT/TTS problem: romanized Hindi stresses both. **We are testing generator + evaluator only
here**; STT/TTS to be validated separately.

### What changes for Hinglish

**Generator** — output language flips to natural romanized Hinglish; the seed/spark machinery
stays English (it's just inspiration). The real lift is **register**: avoid translated/textbook
Hindi and avoid pure English; produce actual code-mix, keep words Indians keep in English
("coffee", "phone", "WhatsApp") in English. Few-shot Hinglish examples anchor this. The output
schema is language-agnostic — no change.

**Evaluator** — the *criteria* are concept-level and survive translation; what must change is
every **illustrative example** (technique lines, trap examples) — those calibrate the judge, so
they're rewritten in Hinglish. The **naturalness** criterion flips meaning to "sounds like real
spoken Hinglish, not translated Hindi or pure English." **Feedback language = Hinglish**, sample
answers = Hinglish (per decision below).

**Structure** — for an experiment, clone into a new spec/key (`pushPullHinglish` etc.) so it
coexists with the English version. Long-term, the cleaner refactor is a `language` dimension on
`ExerciseSpec` — not worth paying for a spike.

### Model recommendations

| Role | Recommended | Why | $/1M (in/out) |
|---|---|---|---|
| Generator | **Claude Sonnet 4.6** | Strong multilingual; still honors `temperature` (variety); structured outputs. Cheap enough to run often. | $3 / $15 |
| Evaluator | **Claude Opus 4.8** | Quality-critical (it *is* the coaching); runs once/attempt; best instruction-following + cultural nuance. | $5 / $25 |
| A/B both | **Gemini 2.x/3** | Genuinely strong on Indic languages; key already wired in litellm. | — |

Gotchas for the Claude path:
1. **Opus 4.8/4.7 reject `temperature` (400)** — `drop_params=True` silently drops it, so it's a
   no-op there. Fine for the generator (entropy comes from spark words), which is why Sonnet 4.6
   (still honors temperature) is the generator pick.
2. Temp 1.0 is too high for a *judge* on non-reasoning models — lower the evaluator to ~0–0.3
   (this harness uses **0.3**). On Opus, prefer adaptive thinking + `effort` over temperature.

Decisions taken: **romanized** (not Devanagari), **feedback in Hinglish**.

---

## Part 2 — What we actually ran

**Model reality on this machine:** only `OPENAI_API_KEY` and `GEMINI_API_KEY` are set
(no Anthropic key → no Claude). The **Gemini key is free-tier with quota exhausted**:
`gemini/gemini-2.5-flash` answers a single probe but a full ~44-call run 429s immediately, and
`2.5-pro` / `2.0-flash` are fully quota-blocked. So both runs used **`gpt-5.3-chat-latest`**
(temp 1.0 generator, 0.3 evaluator).

To properly A/B the recommended models you need either an **Anthropic key** (for Claude) or
**billing enabled** on the Gemini key — then just pass `--gen-model` / `--eval-model`.

---

## Part 3 — Results

### Push-pull (`results.md`)

**Generator: strong.** 22/22 distinct, all romanized, zero Devanagari, genuinely natural
code-mix and register ("PJs", "auto se utarte", "WhatsApp chats scroll karte", "menu dekhte hi
top 3 rank kar leti hai"). Observable and concrete; good spread across appearance / vibe /
behaviour.

**Evaluator: works well.** Correctly detected "no attempt" every time, said so kindly in
Hinglish, and still produced 3 scenario-specific sample answers using the 3 techniques
(compliment→tease / tease→compliment / feigned reluctance), each with a real push + pull, kept
short. The 4-section Hinglish feedback structure held.

**Issues**
- **#13 & #14 are near-duplicates** (both deadpan "straight face se paani sip karti hai"). The
  `unique 22/22` header is *exact-string* match, so it overstates real diversity — semantic
  collisions slip through.
- **Emojis leaked** into several sample answers (😄 😛). The push-pull evaluator prompt didn't
  forbid them (only the generator did). Fixed in the misinterpretation evaluator (see below).

### Misinterpretation (`results_misint.md`)

**Generator: strong, and a particularly good Hinglish fit.** 22/22 distinct, plain everyday
sentences with `main`/`tu`/`tum`/`hum`, each with latent ambiguity a listener can twist
("charge pe laga do", "phone fix kar dena / hang ho raha hai", "table book kar dena",
"dates dekh le", "settle ho jao"). Code-mix actually *helps* here — Hindi+English creates rich
double meanings English-only sentences don't have.

**Evaluator: strong.** Sample answers are genuine misinterpretations — they misread a *specific*
word and commit, across multiple techniques (Literal Trap, Subject Flip, Scope Explosion,
Innuendo). Examples: "charge" → legal charge; "dates dekh le" → fruit; "table book" → a book of
tables; "hum … reply karte hain" → "kitne log milke ek message ka reply karte ho?". 4-section
Hinglish feedback held, **no emojis** (the clamp worked).

**Issues**
- A few samples are mildly forced/borderline, but the large majority pass the litmus test (they
  don't work under the sentence's real meaning).
- Same exact-string-uniqueness caveat: `stretch` appears in #8/#22, `run/gym` themes repeat —
  distinct strings, mildly overlapping content.

---

## Part 4 — Net takeaways & next steps

- **Romanized Hinglish + Hinglish feedback is clearly viable**, even on `gpt-5.3` (not the
  recommended model). Misinterpretation looks like the stronger Hinglish exercise of the two.
- **Fix forward**
  1. Forbid emojis in the push-pull evaluator (already done for misinterpretation).
  2. Replace exact-string uniqueness with a semantic-dup check (catch #13/#14-type collisions),
     or widen seed entropy.
  3. **A/B the recommended models** (Claude Sonnet 4.6 / Opus 4.8, Gemini) once a key with quota
     is available — Indic register is exactly where models diverge.
  4. Validate the deferred **STT (Deepgram) + TTS (OpenAI)** paths for romanized Hindi before any
     real rollout.
  5. If it graduates from spike → product: add real `pushPullHinglish` / `misinterpretationHinglish`
     specs in the backend (or a `language` dimension on `ExerciseSpec`) + `task_catalog` entries.
