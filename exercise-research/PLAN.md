# Exercise Research Plan

Goal: build a master catalog of exercises for storytelling, humour, joke-cracking,
quick wit, improv (theatre + comedy), dating/social skills, oratory, communication,
and tonality — then map which apps/websites/coaches teach which exercises.
Final deliverable: one `.xlsx` with multiple sheets.

All subagents run on **Fable 5** (`model: "fable"`), launched via the Agent tool
with web search enabled, writing outputs to `output/`.

## Directory layout

```
exercise-research/
  PLAN.md
  prompts/
    step1-exercise-discovery.md   # template with {DOMAIN} slot — 8 parallel runs
    step2a-provider-discovery.md
    step2b-provider-analysis.md   # template with {PROVIDER_BATCH} slot
    step2c-coach-program-scrape.md
  output/
    step1/<domain>.jsonl          # one file per domain agent
    step1/<domain>-notes.md       # free-form research notes per agent
    step1/master-exercises.jsonl  # after merge (step 1b)
    step2/providers.jsonl         # step 2a
    step2/provider-exercises/<batch>.jsonl   # step 2b
    step2/coach-programs/<coach>.md + .jsonl # step 2c
  final/
    exercise-research.xlsx        # step 3
```

## Steps

### Step 1 — Exercise discovery (8 parallel subagents, web-heavy)
One prompt template (`prompts/step1-exercise-discovery.md`), instantiated once per
domain. **Deliberately knows nothing about step 2 or any specific provider**, so the
catalog isn't biased toward what coaches already sell.

Domains (one agent each):
1. `storytelling` — narrative craft, personal stories, story structure drills
2. `humor-jokes` — joke writing, comedy writing, stand-up, being funnier in conversation
3. `improv` — improv theatre + improv comedy games, warmups, scene work
4. `quick-wit` — thinking on your feet, verbal agility, comebacks, word games
5. `dating-social` — dating, flirting, banter, social confidence, approach drills
6. `oratory` — public speaking, rhetoric, debate, persuasion, presentations
7. `conversation` — everyday communication, small talk, listening, charisma
8. `voice-tonality` — vocal delivery, tonality, projection, pace, articulation, accent

Each agent targets 60–150 exercises → 500–1000+ total. Sources: improv canon
(Spolin, Johnstone, UCB, Second City), stand-up/comedy-writing books, Toastmasters,
debate clubs, voice/acting pedagogy, dating-coach drills, academic/therapy adjacent
(social skills training), Reddit/forums, blogs, YouTube transcripts.

Output: `output/step1/<domain>.jsonl` (schema in the prompt) + a notes md.

### Step 1b — Merge & ID (no subagent; done in-session with a small Python script)
Concatenate the 8 JSONL files, collapse only **exact-name** duplicates (merging their
domain tags), assign stable IDs `EX-0001…`. Similar-but-distinct exercises are kept,
per your instruction. Output: `output/step1/master-exercises.jsonl`.

### Step 2a — Provider discovery (1 subagent)
Enumerate apps, websites, online programs, coaches, YouTube channels, courses across
all the domains. Seeds: Yoodli, Vocal Image, SmartyMe, Vinh Giang, Todd V Dating —
plus everything it can find (Orai, Speeko, Ultraspeaking, Charisma on Command,
School of Laughs, etc.). Output: `output/step2/providers.jsonl` with type, URL,
domains, pricing model, and a `worth_deep_dive` flag.

### Step 2b — Provider deep-dive (parallel subagents, batched)
After reviewing the 2a list, split providers into batches of ~6–10 by category
(apps / courses / coaches / channels). One prompt template, instantiated per batch.
Each agent documents every exercise/drill/lesson-type the provider offers.
Output: `output/step2/provider-exercises/<batch>.jsonl`.

### Step 2c — Coach program scrape (parallel subagents, one per qualifying coach)
For coaches flagged in 2a/2b as having a structured online program (e.g. Todd V's
program, Vinh Giang's Stage Academy), do a deep scrape: sales pages, curriculum
outlines, module lists, free lead magnets, YouTube descriptions, course-platform
listings, reviews that describe the drills. Output: one md dossier + jsonl per coach.

### Step 2d — App metadata enrichment (parallel subagents, batched) [ADDED]
For every app-type provider (mobile-app / web-app / ai-tool), gather maximum
company/product metadata: launch/founding date, founders, HQ, total funding +
rounds + investors, last valuation, revenue estimate, download/MAU estimates,
employee count, pricing, platforms, acquisition status. Mark confirmed vs estimate
with sources. Output: output/step2/app-metadata/<batch>.jsonl. Feeds an "App
Metadata" sheet in the xlsx and enriches the Providers sheet.

### Launch policy [ADDED]
Run subagents at most **3 concurrent, rolling** — launch the next queued agent as
one completes (not big simultaneous waves). Queue order: Step 2c first, then 2d.

### Step 3 — Compile xlsx (in-session Python, openpyxl/pandas)
Sheets:
1. **Master Exercises** — full step-1 catalog (one row per exercise)
2. **Providers** — step-2a list with analysis status
3. **Provider Exercises** — step 2b/2c rows, with a best-effort `matched_exercise_id`
   linking back to the master catalog where the exercise is clearly the same
4. **Coverage Matrix** — domains × providers, counts of exercises offered

## Execution mechanics

- Step 1: launch all 8 agents in parallel (`run_in_background`), Fable 5.
- Checkpoint after each step: you review outputs before the next step launches
  (especially the 2a provider list, which determines 2b/2c batching).
- Step 1 agents are told to keep searching until they hit diminishing returns,
  not a fixed time budget.
