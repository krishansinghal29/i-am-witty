# Step 2c (corpus variant) — Open Exercise-Corpus Extraction Prompt

> For providers that are large, public, openly-documented exercise corpora (wikis,
> official curricula) rather than a coach selling a gated program.
> Replace `{CORPUS_NAME}`, `{CORPUS_SLUG}`, `{STARTING_POINTS}`, `{TARGET}`.

---

You are extracting as many distinct, well-described exercises as possible from a
large public exercise corpus: **{CORPUS_NAME}**.

Starting points:
{STARTING_POINTS}

## Goal
Walk the corpus and capture every distinct named exercise/game/drill you can, each
with enough instruction to actually run it. Target: **{TARGET}**. This corpus is
public and enumerable — be systematic (e.g. walk index/category pages, then open
individual game pages). Breadth is the point; capture variants as separate entries.

If a page blocks automated fetch, fall back to search snippets, mirrors, or the
Wayback Machine, and mark those entries `inferred`.

## Output
1. Per-exercise JSONL to
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/coach-programs/{CORPUS_SLUG}.jsonl`
   — same schema as step 2b:
   provider ("{CORPUS_NAME}"), exercise_name, description, domains (subset of:
   storytelling, humor-jokes, improv, quick-wit, dating-social, oratory,
   conversation, voice-tonality), format (drill|game|ai-roleplay|
   recorded-speech-with-feedback|writing-prompt|live-session|field-assignment|
   lesson|challenge), evidence (confirmed|inferred), source_urls.
   Write incrementally; validate every line is JSON.

2. A short dossier to
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/coach-programs/{CORPUS_SLUG}.md`
   describing the corpus, how it's organized, how many exercises it contains in
   total vs how many you captured, and coverage gaps.

## Final report
Report: number of exercises extracted, total estimated size of the corpus, evidence
quality, and the richest sub-sections.
