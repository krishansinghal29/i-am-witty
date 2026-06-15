# Step 2b Provider Summaries — Batch: gapfill

Two providers missed in earlier batches: one community public-speaking org
(Agora Speakers International) and one improv-practice mobile app (Yes, And!).

---

## Agora Speakers International
- **Type**: community (non-profit). A Toastmasters-style global public-speaking &
  leadership club, founded 2017 as a free/open alternative, with the same
  speak-evaluate-take-a-role meeting loop but a larger, more granular curriculum.
- **Methodology**: Structured, peer-evaluated, rep-based curriculum on a four-stage
  loop (Learn → Prepare → Practice → Get Evaluation/Feedback → Repeat). Two parallel
  trunks: Communication/Public-Speaking and Leadership. A mandatory 16-project Basic
  Path (three groups: initial / basics of speaking / speaking techniques), then ~20
  Advanced Paths (Storytelling=21 projects, Humorous Speeches, Persuasive, Leadership=23,
  Educational=20, Business=23, Against All Odds=10, Dramatization, etc.). Most basic
  projects are two-part: a speech-analysis half and a speech-delivery half done in
  separate meetings. Meetings layer ~30 named activities (Hot Questions impromptu,
  Crossfire, Club Debate, Colloquium, Role Playing, Today We Travel To, Creativity
  Corner, Language Improvement Games, Thought of the Day) and ~35 evaluator roles.
- **Exercises found**: 35 logged — the 16 basic-path projects, the impromptu/meeting
  activities most relevant to our domains, key evaluator/analysis activities, 7 of the
  most relevant advanced paths, and 2 contests (Storytelling, Humorous).
- **Evidence quality**: Mixed-to-good. Program *structure*, the full project-name list
  (from the public sitemap), meeting roles, meeting format, and the learning loop are
  CONFIRMED from public pages. The per-project objectives/time-limits are member-gated
  (login wall on every project detail page), so individual-project descriptions are
  partly inferred from project names + the Toastmasters analogue.
- **Most relevant to riffy**: Hot Questions (impromptu/quick-wit drill), Using Humour,
  Using Anecdotes, Using Emotion (storytelling technique speeches), Crossfire and the
  "Against All Odds" constraint challenges (Hecklers, Time Warp, etc.), Role Playing,
  and the Storytelling/Humorous advanced paths.
- **2c deep scrape?** MEDIUM — and gated. The full ~200-project curriculum (16 basic +
  ~20 advanced paths) is the single richest non-Toastmasters oratory corpus, but every
  project detail page sits behind a member login, so a scrape needs an account. Without
  one, the public sitemap is the ceiling. Start URL (free, no login): the sitemap and
  the public structural pages — https://www.agoraspeakers.org/sitemap ,
  http://www.agoraspeakers.org/pages/Educational+Program+Overview ,
  http://www.agoraspeakers.org/pages/Meeting+Format . Given Toastmasters Pathways
  already covers this design space, recommend only a LIGHT scrape unless a member login
  is obtained.

## Yes, And! App
- **Type**: mobile-app (iOS) + companion web app (yesandimprov.org). An improv-practice
  "pocket companion" by indie dev noaman mangera. Note: the listed App Store URL
  (apps.apple.com/us/app/yes-and/id6743654613) currently returns not-found in-browser
  (app delisted/region-restricted/renamed); the web app at yesandimprov.org is the live
  primary source and exposes the same content. A separate marketing site exists at
  yesandapp.co.uk.
- **Methodology**: Reps + structured drills + AI partner, organised around six improv
  principles (Play & Have Fun, Yes-And, Make Mistakes Freely, Listen Actively, Be
  Obvious, Commit Fully). Practice is split into 6 modes (Solo Games, Virtual Improviser
  = AI scene partner, Pair Games, Dynamic Duo, Scene Generator, Word Generator) over a
  library of 100 categorised exercises (30 free / 70 Pro), each tagged by difficulty
  (Beginner→Advanced), category (Warm Up / Core Exercise / Fun and Games), and format
  (Solo / Pair / Group). Supporting tools: timers, session recording for self-review,
  random suggestion generator, progress tracking, and a video resource library on 7
  craft concepts (accepting/advancing/making offers, commitment, listening, stakes,
  staging).
- **Exercises found**: 36 logged — the 6 practice modes (incl. the AI Virtual
  Improviser) + 30 named library exercises captured directly from the rendered games
  page (the other 70 are Pro-gated and unnamed publicly).
- **Evidence quality**: Mostly CONFIRMED — the 30 exercise names with their
  difficulty/category/format tags and all 6 practice-mode descriptions were read
  directly from the live rendered site; the app-level feature claims (AI partner adjusts
  to skill, record sessions, 50+ exercises) are confirmed from the App Store listing
  text. Per-exercise step-by-step instructions are login/Pro-gated, so individual
  exercise descriptions are partly inferred from the well-known improv-game canon.
- **Most relevant to riffy**: The Virtual Improviser AI scene partner is the closest
  direct analogue to an AI-roleplay exercise; the Scene Generator / Word Generator are
  trivially portable quick-wit prompts; and the Solo + Beginner-tagged drills (Yes And
  Scene, Three Line Conversation, Word Association, New Choice, Eight Things About Me)
  are clean solo-practiceable exercises.
- **2c deep scrape?** YES (light, free). The games library is JS-rendered but readable
  with a browser tool, and signing up for a free account unlocks the full 100-exercise
  list (currently only 30 named publicly) plus per-exercise instructions. Start URL:
  https://yesandimprov.org/games (render with browser; "Sign Up For Free" unlocks +70).
  Also https://yesandimprov.org/practice for the 6 mode definitions.
