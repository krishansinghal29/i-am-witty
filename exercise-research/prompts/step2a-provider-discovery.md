# Step 2a — Provider Discovery Subagent Prompt

---

You are a research agent compiling the most complete possible list of **providers**
that teach or train people in any of these skill domains:

storytelling, humor / joke writing / stand-up, improv (theatre and comedy),
thinking on your feet / quick wit, dating and social confidence, public speaking /
oratory / persuasion, everyday conversation and communication, voice and tonality.

"Provider" means anything a person could pay for or follow to get exercises and
training: mobile apps, web apps, online course platforms and specific courses,
individual coaches with programs, YouTube channels/educators, podcasts with
practice components, in-person schools with online arms (UCB, Second City,
Toastmasters), AI practice tools, books-with-companion-programs, communities with
structured practice (e.g. story slams, rejection therapy communities).

## Known seeds (verify and include, then go far beyond them)

Yoodli, Vocal Image, SmartyMe, Vinh Giang (Stage Academy), Todd V Dating.

Other names likely relevant — verify and expand: Orai, Speeko, Ummo, Poised,
Ultraspeaking, Charisma on Command / Charisma University, The Moth (workshops),
Storyworthy / Matthew Dicks (Homework for Life), Greg Dean stand-up courses,
Comedy Bites / online improv schools (Hoopla, Improv Asylum online), Toastmasters,
School of Connection, The Art of Charm, Improvement Pill, Communication coaches on
Maven/Udemy/Skillshare/MasterClass (e.g. Chris Voss, Robin Roberts MasterClass),
dating coaches with structured programs, AI conversation-practice apps.

## How to search

- Per-domain queries: "best apps to improve public speaking", "online stand-up
  comedy course", "AI dating conversation practice app", "improv classes online",
  "voice training app", etc. — multiple phrasings each.
- App Store / Google Play category mining (search results pages are indexable).
- Product Hunt, AlternativeTo, "X alternatives" articles.
- Course platforms: Udemy/Skillshare/Coursera/MasterClass/Maven catalog searches.
- Reddit "what app/course actually helped you" threads.
- For coaches: YouTube channels in each niche, then check if they sell a program.

Target: **80–200 providers**. Breadth over depth — deep analysis is a later step.
Spend only ~2–4 minutes per provider: enough to classify it and judge whether it
actually offers exercises/practice (vs. pure content/entertainment).

## Output format

Write to:
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/providers.jsonl`

One JSON object per line:

```json
{
  "name": "Provider name",
  "type": "mobile-app | web-app | ai-tool | online-course | coach-program | youtube-channel | school | community | book-program | podcast",
  "url": "primary URL",
  "domains": ["from: storytelling, humor-jokes, improv, quick-wit, dating-social, oratory, conversation, voice-tonality"],
  "pricing": "free | freemium | subscription | one-time | high-ticket | unknown (add price if visible, e.g. 'subscription ~$10/mo')",
  "offers_exercises": "yes | partially | content-only | unknown",
  "what_it_is": "1-2 sentence description",
  "has_structured_program": "yes | no | unknown — does a coach/channel sell a curriculum-based online program?",
  "worth_deep_dive": "high | medium | low — how promising for detailed exercise extraction",
  "notes": "anything useful for the deep-dive step, e.g. 'curriculum page public', 'app store screenshots show drill types'"
}
```

Write incrementally; validate JSON. Also write a short summary md to
`/Users/krishansinghal/i-am-witty/exercise-research/output/step2/providers-notes.md`
listing per-domain coverage and any categories you suspect are under-explored.

## Final report

Report back: total providers found, count per type, count per domain, and your
top-15 `worth_deep_dive: high` picks with one line each on why.
