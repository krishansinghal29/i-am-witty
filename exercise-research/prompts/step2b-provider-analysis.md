# Step 2b — Provider Deep-Dive Subagent Prompt

> Template. Replace `{BATCH_NAME}` and `{PROVIDER_BATCH}` per run.
> Batches are formed after reviewing step 2a output: ~6–10 providers per agent,
> grouped by type (apps together, coaches together, etc.).

---

You are a research agent doing a detailed analysis of what specific **exercises,
drills, lessons, and practice activities** each of the following providers offers.

Providers in your batch ({BATCH_NAME}):

{PROVIDER_BATCH}
<!-- paste the relevant JSONL lines or a name+url+notes list from step 2a -->

## For each provider, find out

1. **Catalog of exercises/drills**: every distinct practice activity you can
   identify — named drills, lesson types, game modes, AI roleplay scenarios,
   assignments, challenges. For apps, mine: app store listings and screenshots,
   feature pages, help docs/FAQ, changelogs, review sites, YouTube walkthroughs
   and reviews ("Yoodli review", "Vocal Image app walkthrough"), Reddit user
   reports. For courses/coaches: curriculum pages, module lists, free previews,
   lead magnets, podcast interviews where they describe their method.
2. **Methodology**: what's their theory of improvement (reps + AI feedback?
   structured curriculum? live practice? field assignments?).
3. **Format & pricing details**: refine what step 2a found if you learn more.

Be honest about evidence quality: mark whether each exercise is confirmed (seen
directly in screenshots/docs/curriculum) or inferred (from reviews/descriptions).

## Output format

Write to:
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/provider-exercises/{BATCH_NAME}.jsonl`

One JSON object per exercise per provider:

```json
{
  "provider": "Provider name (exactly as in step 2a)",
  "exercise_name": "Name the provider uses, or a descriptive name if unnamed",
  "description": "what the user actually does",
  "domains": ["from: storytelling, humor-jokes, improv, quick-wit, dating-social, oratory, conversation, voice-tonality"],
  "format": "drill | game | ai-roleplay | recorded-speech-with-feedback | writing-prompt | live-session | field-assignment | lesson | challenge",
  "evidence": "confirmed | inferred",
  "source_urls": ["where you saw it"]
}
```

Also append one provider-level summary per provider to
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/provider-exercises/{BATCH_NAME}-summaries.md`:
~10 lines each covering methodology, exercise count found, evidence quality, and
whether a step-2c deep scrape of a structured program is warranted (and what URL
to start from).

## Final report

Report back: per provider — number of exercises found, evidence quality
(mostly confirmed vs mostly inferred), and your 2c recommendation (yes/no + URL).
