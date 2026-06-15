# ✅ PIPELINE COMPLETE (2026-06-10) — final/exercise-research.xlsx built

All steps done. Final xlsx: 6 sheets — Overview, Master Exercises (993),
Providers (128), App Metadata (45), Provider Exercises (1446 deduped, 84 matched),
Coverage Matrix (82 providers). Rebuild anytime: `.venv/bin/python scripts/compile_xlsx.py`.
Re-merge step1: `python3 scripts/merge_step1.py`. Everything below is historical log.

# Pipeline run state (autonomous run, started 2026-06-10)

User instruction: complete ALL steps without asking anything. All subagents on Fable 5.

## Launched (running in background)

Step 1 agents (one per domain) + step 2a, launched in parallel:

| agentId | task |
|---|---|
| aaab00620ded4ee2d | step1 storytelling |
| aba400a569849dd97 | step1 humor-jokes |
| a0eba1792021f8337 | step1 improv |
| acc8e0257e08b1e7f | step1 quick-wit |
| a8b0a7b00e70712f5 | step1 dating-social |
| a54bda439a7ca9879 | step1 oratory |
| adcffda7933114d23 | step1 conversation |
| a23939131904ae6a7 | step1 voice-tonality |
| af0ef2290d4aa31b5 | step2a provider discovery |

## Step 1 — first pass cut off by usage limits, RESUMED on Opus 4.8

First pass left valid partial output on disk (573 exercises total, all JSON-valid).
No SendMessage/continue-agent tool exists in this env, so resume = fresh agents
reading existing files + appending (prompts/step1-resume.md). Running to diminishing
returns per user. Step 2a fully completed first pass (128 providers) — not resumed.

Resume agents (Opus 4.8, background), with pre-resume counts:

| agentId | domain | had |
|---|---|---|
| a0e44a21137808c73 | humor-jokes (canary) | 61 |
| a0913ab6ffabd0df7 | storytelling | 76 |
| af91a2f58a0eb54b3 | improv | 95 |
| a4af31713d4b31219 | quick-wit | 69 |
| a0ca05eed62051d99 | dating-social | 73 |
| a4a14f0f1a62af60b | oratory | 64 |
| a50a8ecd0275c28c5 | conversation | 67 |
| a6d1711a0dc2e5694 | voice-tonality | 68 |

Model note: user switched to Opus 4.8 ("from now on use opus 4.8") — applies to all
remaining agents (step 2b/2c) and in-session work.

## PROGRESS LOG

- Step 1: DONE. 1045 raw exercises across 8 domains, all resumed on Opus to
  diminishing returns. Final per-domain: storytelling 128, humor-jokes 104,
  improv 183, quick-wit 113, dating-social 120, oratory 140, conversation 129,
  voice-tonality 128.
- Step 1b: DONE. output/step1/master-exercises.jsonl = 993 unique (52 exact-name
  dups collapsed, 48 multi-domain). IDs EX-0001..EX-0993.
- Step 2a: DONE earlier. 128 providers.
- Step 2b: LAUNCHED (13 batches, Opus, background). Mapping below. Batches built
  from 82 high+medium providers via scripts/make_batches.py; subset files in
  output/step2/batches/. Each agent writes
  output/step2/provider-exercises/<batch>.jsonl + <batch>-summaries.md and reports
  a 2c recommendation per provider.

| agentId | batch |
|---|---|
| a94315657497fc6a9 | apps-1 |
| a5ef56039183edba3 | apps-2 |
| ab774507171a0e3c4 | apps-3 |
| abc841ca33e81426d | apps-4 |
| a708c99db023dac37 | courses-1 |
| af66c70cca7ddc9a4 | courses-2 |
| a2c418099f7d56a6f | courses-3 |
| a08dca4c50f6d2121 | schools-1 |
| aa65d22e9e78d72ea | schools-2 |
| ab0e8017e9769cb3d | coaches-1 |
| ad05415081e013ca0 | coaches-2 |
| aac71ade9bac4a70a | community-1 |
| ac781df1c3cb121cb | community-2 |

## ▶ RESUMED 2026-06-10 — all-at-once waves now (user lifted the rolling-3 rule)

User: "launch all 2c in one go and then all 2d in one go ... for improv-encyclopedia
take a call whether to rerun ... then go ahead with step 3 ... don't ask questions."

DECISION improv-encyclopedia: REVISED per user ("rerun unless signal it completed;
very important"). It hit a session limit (no clean-finish signal) at 160 games, so
RESUMING it (read existing 160, dedupe, extend to 280-350+, write the missing .md).
  - improv-encyclopedia RESUME   agentId a11ae6d919beae29d  (appends to same jsonl)

2c WAVE: ALL DONE — patrick-king(38) todd-v-dating(25) vinh-giang(32)
  charisma-university(34) art-of-charm(34).

2d WAVE launched all 5 at once (improv-encyclopedia resume still topping up in
parallel; 2d is independent of it):
- meta-1  a9b188b7e5859753c
- meta-2  a176a8e25005b25d5
- meta-3  a13d5c2ff91b4bbf6
- meta-4  a48d2cba31373061e
- meta-5  aaa611c17247b72f4

2d WAVE: ALL DONE (meta-1..5, 45 apps).
ONLY REMAINING in flight: improv-encyclopedia resume (agentId a11ae6d919beae29d) —
actively appending (was 160, ~328+ now).

Step 3 READY: scripts/compile_xlsx.py written; run with
`.venv/bin/python scripts/compile_xlsx.py` -> final/exercise-research.xlsx.
DO NOT run until improv-encyclopedia resume reports done. .venv has openpyxl.
Compile handles: provider canonicalization (merge 2b+2c, e.g. Greg Dean / Toastmasters),
within-provider exercise dedupe, matched_exercise_id back-links, App Metadata sheet,
Coverage Matrix. Sheets: Overview, Master Exercises, Providers, App Metadata,
Provider Exercises, Coverage Matrix.

2c DONE on disk: greg-dean(39) toastmasters-pathways(83) matthew-dicks(28)
  judy-carter(30) improv-encyclopedia(160→resuming) patrick-king(38)
  todd-v-dating(25) vinh-giang(32) charisma-university(34) art-of-charm(34)

## ROLLING QUEUE (max 3 concurrent — launch next on each completion)

User directive (mid-run): never more than 3 subagents at once; as one finishes,
launch the next from this queue. Also NEW step 2d = app metadata. Then step 3 xlsx
LAST (so it includes 2c+2d).

IN FLIGHT now (let finish, do NOT replace on completion — PAUSED):
- 2c improv-encyclopedia (corpus)             agentId a55ea3fee5debc2e1

DONE: gapfill (71) | greg-dean (39) | toastmasters-pathways (83) | matthew-dicks (28) | judy-carter (30)
  NOTE: toastmasters-pathways.jsonl supersedes the 18 "Toastmasters International"
  rows in community-1.jsonl — dedupe/keep-pathways at xlsx time.

QUEUE (launch in order as slots free):
2c coaches (template prompts/step2c-coach-program-scrape.md; starting points from 2b reports):
  [x] greg-dean        — DONE 39 ex
  [x] matthew-dicks    — LAUNCHED ad33de2093e0f2877
  [x] judy-carter      — LAUNCHED a821bc3a33f8c1f0c
  [ ] patrick-king     — Internet Archive full text of Witty Banter / Improve Your Conversations (HPM/SBR/EDR, free association)
  [ ] todd-v-dating    — verbalgameacademy.com + toddvdating.com/category/verbal-game-academy/ (VGA 8-week map) [SEED]
  [ ] vinh-giang       — YouTube @askvinh + 5 Vocal Foundations video; stage.academy [SEED]
  [ ] charisma-university — charismaoncommand.university/lds-course-notes/ (day-by-day field assignments)
  [ ] art-of-charm     — theartofcharm.com/category/podcast-episodes/toolbox-episodes/ + join.theartofcharm.com/xfa
2d app metadata (template prompts/step2d-app-metadata.md; batch files in output/step2/app-metadata/batches/):
  [ ] meta-1  [ ] meta-2  [ ] meta-3  [ ] meta-4  [ ] meta-5

After queue empties: Step 3 — compile final/exercise-research.xlsx (sheets:
Master Exercises, Providers, App Metadata, Provider Exercises w/ matched_exercise_id,
Coverage Matrix).

## Remaining pipeline (do autonomously as agents complete)

1. **Step 1b** (after all 8 step-1 agents done): in-session Python — concat
   output/step1/*.jsonl, validate JSON, collapse exact-name dupes (merge domain
   tags), assign IDs EX-0001…, write output/step1/master-exercises.jsonl.
   If an agent died leaving a partial/empty file, relaunch just that domain once.
2. **Step 2b** (after 2a done): read output/step2/providers.jsonl, group
   worth_deep_dive high+medium providers into batches of ~6-10 by type, launch
   one agent per batch using prompts/step2b-provider-analysis.md with
   {BATCH_NAME} and {PROVIDER_BATCH} (paste the JSONL lines) filled in.
   Output: output/step2/provider-exercises/<batch>.jsonl. Fable 5, background.
3. **Step 2c** (after 2b): collect 2c recommendations from batch reports +
   *-summaries.md; launch one agent per recommended coach using
   prompts/step2c-coach-program-scrape.md ({COACH_NAME}, {COACH_SLUG},
   {STARTING_POINTS}). Cap at ~8 coaches, prioritize by promise. Must include
   seeds if flagged: Todd V, Vinh Giang, plus e.g. Charisma University.
4. **Step 3** (after 2c): in-session Python (pandas/openpyxl, pip install if
   needed) → final/exercise-research.xlsx with sheets:
   Master Exercises / Providers / Provider Exercises / Coverage Matrix.
   Provider Exercises gets best-effort matched_exercise_id via normalized name
   matching against master list (exact + alias match only; leave blank if no match).
5. Final summary to user with counts per sheet.
