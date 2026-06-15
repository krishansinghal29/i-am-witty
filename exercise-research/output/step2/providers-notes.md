# Step 2a — Provider Discovery Notes

Date: 2026-06-10. Total providers: **128** (`providers.jsonl`, one JSON object per line, all validated).

## Per-domain coverage (a provider can count in multiple domains)

| Domain | Count | Coverage assessment |
|---|---|---|
| conversation | 43 | Strong. AI feedback tools, roleplay apps, courses, communities all represented. |
| oratory | 42 | Strongest/most crowded market. AI speech coaches are commoditized (filler words, pace). |
| dating-social | 27 | Good. Two distinct clusters: coach programs (Todd V, Hussey, Hayley Quinn) and AI "rizz" reply-generators. Practice-by-simulation (Blush) and exposure ladders (Rejecto) are the interesting middle. |
| humor-jokes | 23 | Good on stand-up schools/courses; thin on *conversational humor* products. Only Udemy/Skillshare courses + books target everyday funniness. |
| storytelling | 21 | Good. Matthew Dicks ecosystem is the densest exercise source. Business-storytelling (Duarte, Kindra Hall, ABT) is a separate sub-market. |
| improv | 18 | Good on schools; very thin on apps (Yes And!, Suggestifier are tiny). Improv Encyclopedia is the open exercise corpus. |
| quick-wit | 17 | **Weakest as a product category.** Mostly books (Patrick King), impromptu-speaking games (Ultraspeaking, Table Topics), and one-off Udemy courses. No dominant dedicated wit-training app found — whitespace for riffy. |
| voice-tonality | 10 | Adequate. Vocal Image dominates consumer; rest are coach programs (Roger Love, Vocal Awareness) or clinical tools. |

## Per-type counts

mobile-app 24 · online-course 29 · school 21 · ai-tool 18 · coach-program 15 · community 9 · podcast 5 · web-app 3 · youtube-channel 3 · book-program 1

## Under-explored categories / gaps to revisit

- **Quick-wit dedicated tools**: searches for "witty comeback practice app" return listicles and AI generators (ComebackPro), not trainers. Strong signal of market whitespace; worth a second mining pass on app stores with queries like "banter", "wit", "comebacks", "rizz trainer".
- **Non-English / non-US providers**: only UK (Hoopla, Logan Murray, Hayley Quinn, Project Charisma) lightly covered; Aussie/Indian communication-coach markets (e.g., Kapable) not enumerated.
- **TikTok/Instagram educators** with paid programs (humor/dating niches) — not mined at all; discovery there needs platform search.
- **Skillshare/Coursera catalogs**: only spot-checked; a systematic catalog crawl would add 20-50 long-tail courses (diminishing returns for exercise novelty, but cheap curriculum mining).
- **Corporate L&D roleplay platforms** (Skillsoft CAISY, LinkedIn Learning AI roleplay, Coachello, Kendo, Outdoo, Revarta, Virti, Second Nature, Quantified): deliberately kept to representatives only — B2B sales-skew, low exercise novelty.
- **Speech-therapy / accent apps** (BoldVoice, Tactus Conversation Therapy): adjacent; included representatives only.
- **Seed not verified**: "Comedy Bites" could not be confirmed as an existing improv/comedy provider (searches return UCB/WGIS etc. and an unrelated driving school). Possibly defunct or misremembered name. "School of Connection" likewise did not resolve to a distinct findable program; nearest matches are unrelated kids' SEL programs — flagging rather than fabricating an entry.
- **Story slam ecosystem beyond The Moth** (regional slams: Story District covered; First Person Arts, The Stoop, Backyard Story Night etc. not enumerated) — low marginal value, same exercise patterns.

## Observations useful for the deep-dive step

1. Richest documented exercise corpora: Improv Encyclopedia (free, hundreds of games), Judy Carter's Comedy Bible Workbook (48 named exercises), Matthew Dicks (Homework for Life, Crash & Burn, First/Last/Best/Worst), Ultraspeaking's named games, Toastmasters Table Topics, Patrick King's HPM/SBR free-association drills.
2. Recurring product patterns: (a) AI delivery-feedback (commodity), (b) AI roleplay scenario practice, (c) prompt/game-based impromptu drills, (d) daily micro-challenge ladders (Rejecto/Social Challenge), (e) cohort + homework (Maven/Gotham), (f) email-drip exercises (StoryLab).
3. Udemy/Skillshare course outlines are publicly visible — cheap way to extract curricula without purchase.
