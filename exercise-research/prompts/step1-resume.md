# Step 1 — Resume Subagent Prompt

> Template for resuming a domain whose first agent was cut off by a usage limit.
> Replace `{DOMAIN}`, `{DOMAIN_SCOPE}`, `{DOMAIN_SEEDS}`, and `{EXISTING_COUNT}`.

---

You are RESUMING an interrupted research run. A prior agent already began compiling
an exhaustive catalog of **practical exercises** for the domain **{DOMAIN}** and
wrote **{EXISTING_COUNT}** exercises to this file before it was cut off:

`/Users/krishansinghal/i-am-witty/exercise-research/output/step1/{DOMAIN}.jsonl`

## First, load what's already there

1. Read that JSONL file in full. Each line is one exercise object.
2. Build a mental set of the exercise `name`s (and `aliases`) already captured.
   These are DONE — do not re-add them.

## Then continue the research

Your job is to APPEND new, not-yet-captured exercises to the SAME file, continuing
until you genuinely hit diminishing returns (searches surfacing only exercises
already in the file). Do not stop at a fixed count — the goal is exhaustive
coverage. The prior agent likely stopped well short of exhaustion.

Domain scope: {DOMAIN_SCOPE}

### What counts as an exercise
A concrete, repeatable activity a person can DO to improve — alone, in a pair, or in
a group: drills, games, warmups, writing prompts, speaking challenges,
record-and-review routines, roleplay, field exercises, rehearsal techniques,
feedback rituals. NOT: vague advice, theory, mindset reframes with no activity, or
product features. Turn any actionable advice INTO a concrete drill.

### Where to look (widen beyond what the prior agent covered)
Cast the widest net possible — any source, tradition, or community is in scope.
Seeds (not boundaries; the best material is usually elsewhere): {DOMAIN_SEEDS}
Plus: Reddit, Quora, blogs/listicles, book TOCs and summaries, YouTube
titles/transcripts, university syllabi, workshop agendas, PDF teacher handouts
(`filetype:pdf {DOMAIN} exercises`), wikis, forums. Mine exercise NAMES you find as
new search queries; chase cited books/teachers for their exercise lists. Since the
file already has the obvious entries, deliberately push into less-common sources,
sub-niches, and non-English-origin traditions to find fresh material.

Similar/overlapping exercises are FINE — capture variants separately if they have a
different name, source, or procedure. Do NOT organize research around commercial
apps/coaches/paid programs; catalog the exercises themselves from any source.

## Output — append to the same file
Append one JSON object per line (same schema the existing lines use) to
`/Users/krishansinghal/i-am-witty/exercise-research/output/step1/{DOMAIN}.jsonl`.
Schema fields: name, aliases, domain ("{DOMAIN}"), also_helps (subset of:
storytelling, humor-jokes, improv, quick-wit, dating-social, oratory, conversation,
voice-tonality), description, instructions, format (solo|pair|group|any),
duration_minutes, difficulty (beginner|intermediate|advanced), setup, skill_targets,
origin, source_urls, variations.
Write incrementally (append batches as you go). Every line must be parseable JSON.
Do NOT rewrite or reorder existing lines — only append.

Also write a notes file (the prior agent never got to this):
`/Users/krishansinghal/i-am-witty/exercise-research/output/step1/{DOMAIN}-notes.md`
covering richest sources, sources you couldn't fully mine, queries that worked, and
honest coverage gaps.

## Final report
Report back: how many NEW exercises you appended, the new total in the file, the 5
richest sources, and any sub-areas still under-covered.
