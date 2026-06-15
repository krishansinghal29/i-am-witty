# Step 2b Provider Summaries — Batch: apps-2

## Social Challenge App (socialchallengeapp.com)

- **Methodology**: Graded real-world exposure / rejection therapy grounded in CBT. Theory of improvement = repeated small in-the-field social exposures, escalating in difficulty, with reflection + community reinforcement. Not record-and-feedback; the "rep" happens offline in the real world.
- **Exercises found**: 5 distinct mechanics (daily personalized quest, location-tagged challenges across 16 settings, themed challenge paths/tracks, difficulty-tiered exposure ladder with ranks, progress tracking + community). Individual challenges are generated/personalized rather than a fixed enumerable catalog.
- **Evidence quality**: Mostly confirmed from the marketing site, but only one concrete challenge example is public ("Order coffee and make eye contact"). The full challenge library is behind the app (launching 2025), so the breadth of actual prompts is inferred.
- **2c deep scrape**: YES — worth it for the *engine design* (personalization + difficulty ladder + path structure) rather than a static curriculum. Start URL: https://socialchallengeapp.com/ . Supplement with App Store screenshots once live; the generated-challenge taxonomy is the valuable artifact for a field-assignment feature.

## Wellspoken — Articulation Coach (wellspoken.me / App Store id6752822613)

- **Methodology**: Concept → record yourself → instant AI feedback loop, plus a measurable score (Wellspoken Index /1000 on filler rate, pronunciation, structure, pace). Reps + AI feedback + structured curriculum. Strongest structured taxonomy in this batch and closest to the target product shape.
- **Exercises found**: 9 (Structured Daily Practice, Mock Interviews, Difficult-Conversation/Meeting Roleplay, Impromptu Speaking, Filler Eliminator, Lexicon Flash, Daily 60, Wellspoken Index scoring + meeting capture, curriculum modules Articulate/Eloquent/Nuance/Concise). Several have crisp branded names — ideal for naming inspiration.
- **Evidence quality**: Mostly confirmed — drill names and mechanics appear directly in the landing page and App Store listing; reinforced by a press profile of the founder.
- **2c deep scrape**: YES — this is the single best 2c target in the batch. Start URL: https://www.wellspoken.me/ then walk every named feature page + the App Store description. Goal: extract the full drill taxonomy and the Index scoring rubric.

## Convo — Social Skills Builder (App Store id6749592243)

- **Methodology**: Bite-sized daily speaking exercises to build social "muscle memory", plus guided conversation practice and confidence lessons. Explicitly markets itself as "no awkward roleplay" — i.e. lighter-weight speaking drills over heavy simulation. Reps + feedback + micro-lessons.
- **Exercises found**: 5 (short daily speaking exercise, guided conversation practice on real-world scenarios, conversation-starters practice, confidence-building lessons, speech feedback). Categories are confirmed but the App Store copy deliberately withholds concrete drill breakdowns.
- **Evidence quality**: Mixed — feature *areas* confirmed from the listing; the actual session structure and specific drills are inferred (no screenshots-level detail surfaced; new app).
- **2c deep scrape**: MAYBE / LOW priority — content is thin publicly and overlaps heavily with Wellspoken/Convo-style apps. Only worth it if we can get inside the app for screenshots. Start URL if pursued: https://apps.apple.com/us/app/social-skills-builder-convo/id6749592243 (need in-app capture to add value).

## Speaking.games (Storylab) (speaking.games)

- **Methodology**: Free, directly-playable rapid prompt games (Ultraspeaking-style). Theory = high-volume reps of spontaneous-speaking micro-challenges, organized into three skill buckets: Confidence, Clarity, Delivery. Pure game mechanics, no curriculum, no login wall.
- **Exercises found**: 11 fully-named games with clear mechanics — Impromptu Speech, Slides from Hell, Impossible Questions (Confidence); Explain to a Child, Story Spark, Analogy Machine, Framework Master, Compressor (Clarity); Tongue Twister Battle, Character Swap, Emotion Switch (Delivery). Several map directly to our humor/quick-wit/improv domains.
- **Evidence quality**: Confirmed — every game and its mechanic was read directly off the live site.
- **2c deep scrape**: YES (light) — already mostly captured here, but worth a 2c to *play each game* and document exact prompt formats, timer lengths, and feedback per game. This is the closest analog to a solo-wit game library and the cheapest to fully reverse-engineer. Start URL: https://speaking.games/

## Blush — AI Dating Simulator (blush.ai)

- **Methodology**: Practice-by-simulation. No lessons, no scoring, no structured curriculum — pure open-ended chat with 1,000+ AI "crushes" (distinct personalities/backstories) that adapt to the user. A licensed couples therapist designed character backstories and conflict responses so the sim surfaces realistic relationship dynamics. Theory = you learn dating/communication skills by doing them in a consequence-free environment and noticing your own patterns.
- **Exercises found**: 4 model "modes" rather than discrete exercises (open-ended crush conversations, first-date simulation, conflict/misunderstanding navigation, flirting/approach experimentation). It is the purest "safe practice" dating product but the least enumerable.
- **Evidence quality**: Confirmed at the model level (site + TechCrunch); but because there is no exercise catalog, individual "scenarios" are inferred from how the sim behaves rather than a published list.
- **2c deep scrape**: NO (or low) — there is no structured program to scrape; the value is the *interaction-design pattern* (adaptive characters + therapist-tuned conflict), which is already captured. Only revisit if we want to study its onboarding/persona system hands-on. Start URL if pursued: https://blush.ai/

## VirtualSpeech — AI Roleplays product line (virtualspeech.com/ai-practice)

- **Methodology**: Structured library of 40+ AI roleplay scenarios (55+ exercises total) across soft-skills domains, each with instant AI feedback (filler words, pace, etc.) plus a two-way AI coach debrief. Reps + AI feedback + scenario taxonomy + (separately) courses. The public scenario taxonomy is exactly the kind of exercise-extraction target the template calls out.
- **Exercises found**: 12 captured here (difficult conversations, business negotiation, investor pitch, sell-a-generic-product, job interview, mentoring, customer service, impromptu slide/table-topics, presentation delivery, elevator pitch, event/wedding speeches, AI coach debrief). The real catalog is larger (40+ scenarios) — these are the representative named ones.
- **Evidence quality**: Mostly confirmed from search snippets and the AI-practice page summaries; full per-scenario detail is partly inferred because the site repeatedly refused automated fetch (ECONNREFUSED). Numbers (40+/55+) are from VirtualSpeech's own copy.
- **2c deep scrape**: YES — the most complete published scenario taxonomy in the batch and a direct analog for a roleplay-exercise feature. Start URL: https://virtualspeech.com/practice (and /ai-practice). NOTE: site blocks WebFetch — a 2c run will need a real browser (claude-in-chrome) or manual capture to enumerate all 40+ scenarios.
