# Step 2c — Coach Program Deep-Scrape Subagent Prompt

> Template. Replace `{COACH_NAME}`, `{COACH_SLUG}`, and `{STARTING_POINTS}` per run.
> One agent per coach/program flagged in 2a/2b as having a structured online
> program (e.g. Todd V's program, Vinh Giang's Stage Academy, Charisma University).

---

You are a research agent building a dossier on the online program(s) sold by
**{COACH_NAME}**, with the goal of reconstructing the program's curriculum and
every practice exercise/drill it contains, from publicly available information.

Starting points from earlier research:

{STARTING_POINTS}
<!-- URLs + notes from steps 2a/2b -->

## Where to dig

- Sales/landing pages: module lists, curriculum outlines, "what you get" sections,
  archived versions on web.archive.org if the live page is vague.
- Free funnel content: lead magnets, free PDFs, webinars, email-course signups
  (describe what they advertise; do NOT sign up with any credentials).
- The coach's YouTube channel: video titles/descriptions/transcripts often walk
  through the same drills taught in the paid program.
- Podcast guest appearances where they explain their method.
- Reviews and student write-ups: Reddit, Trustpilot, forum threads, "is X worth it"
  blog posts — students often enumerate the assignments and drills.
- Course-platform listings (Teachable/Kajabi/Udemy pages can expose lecture lists).

Stay within public information. No purchases, no account creation, no paywall
circumvention. If the curriculum simply isn't public, say so and report what the
evidence supports.

## Output

1. Dossier:
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/coach-programs/{COACH_SLUG}.md`
   - Who the coach is, niche, audience
   - Program(s): name, price, format (videos/live calls/community/assignments)
   - Reconstructed curriculum (module by module, as far as evidence allows)
   - Their methodology / theory of improvement
   - Evidence quality assessment

2. Exercise list:
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/coach-programs/{COACH_SLUG}.jsonl`
   — same schema as step 2b (provider / exercise_name / description / domains /
   format / evidence / source_urls), `evidence` being `confirmed` only when a
   drill is directly described in public material.

## Final report

Report back: programs found, curriculum reconstruction confidence (high/med/low),
number of exercises extracted, and the single best public source you found.
