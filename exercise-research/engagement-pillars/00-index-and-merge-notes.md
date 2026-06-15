# Engagement Pillars — Master Catalog Index & Merge Notes

This is the deduplicated master catalog synthesized from nine domain research files. The full catalog is in [`engagement-pillars-catalog.csv`](./engagement-pillars-catalog.csv) (296 rows, columns: `id, pillar_name, meta_category, sub_category, definition, why_it_works, product_examples, how_to_apply, dark_pattern, domains_seen, sources`).

## Raw → Final counts

| Source file | Raw pillars |
|---|---|
| 01-games-f2p | 46 |
| 02-duolingo-edtech | 42 |
| 03-meditation-habit-wellness | 38 |
| 04-behavioral-science-theory | 48 |
| 05-gambling-slots | 32 |
| 06-social-media-shortform | 38 |
| 07-social-multiplayer-roleplay | 38 |
| 08-fitness-kids-playful | 38 |
| 09-friction-onboarding-motivation | 38 |
| **Total raw** | **358** |
| **Final unique pillars** | **296** |

358 raw entries collapsed to **296 unique pillars** — a ~17% reduction. The merge was deliberately conservative (the brief warned that losing pillars to aggressive merging is worse than keeping near-duplicates), so most consolidation happened on the high-overlap foundational mechanics (variable reward, loss aversion, streaks, near-miss, IKEA/endowment, goal-gradient) that every domain independently re-described.

## Meta-category distribution (taxonomy order)

| # | Meta-category | Pillars |
|---|---|---|
| 1 | Behavioral Theory & Foundations | 38 |
| 2 | Core Loops & Feedback | 10 |
| 3 | Reward Systems & Reinforcement | 11 |
| 4 | Progression & Mastery | 17 |
| 5 | Goals, Streaks & Habit Formation | 19 |
| 6 | Loss Aversion, Scarcity & Investment | 9 |
| 7 | Social Connection & Belonging | 30 |
| 8 | Competition & Status | 10 |
| 9 | Identity, Self-Expression & Ownership | 10 |
| 10 | Collection & Completion | 6 |
| 11 | Narrative, Roleplay & Imagination | 14 |
| 12 | Companionship & Parasocial | 11 |
| 13 | Delight, Surprise & Personality | 11 |
| 14 | Friction Reduction & Onboarding | 34 |
| 15 | Triggers, Notifications & Re-engagement | 14 |
| 16 | Personalization & Algorithmic Curation | 13 |
| 17 | Compulsion Engineering & Dark Patterns | 39 |
| | **Total** | **296** |

## Cross-domain pillars (appeared in 4+ source domains) — the universal levers

These are the highest-signal, most-transferable engagement mechanics: every one was independently re-described across at least four of the nine research domains.

| Pillars | Domains | Where it showed up |
|---|---|---|
| **P002 Variable-Ratio Reinforcement** | **8** | games; duolingo-edtech; meditation-habit; theory; gambling; social-media; social-roleplay; fitness-kids |
| **P044 Daily Streaks** | **7** | games; duolingo-edtech; meditation-habit; gambling; social-media; social-roleplay; fitness-kids |
| **P024 Loss Aversion** | **6** | theory; duolingo-edtech; meditation-habit; gambling; social-media; fitness-kids |
| **P070 Variable / Intermittent Rewards (Applied)** | **5** | games; duolingo-edtech; meditation-habit; social-media; fitness-kids |
| **P025 Endowment Effect** | **4** | theory; meditation-habit; gambling; fitness-kids |
| **P026 Sunk-Cost Fallacy** | **4** | theory; meditation-habit; gambling; social-roleplay |
| **P027 Goal-Gradient Effect** | **4** | theory; games; duolingo-edtech; meditation-habit |
| **P028 Endowed-Progress Effect** | **4** | theory; games; duolingo-edtech; friction-onboarding |
| **P032 Peak-End Rule** | **4** | theory; duolingo-edtech; meditation-habit; fitness-kids |
| **P034 IKEA Effect** | **4** | theory; meditation-habit; social-roleplay; fitness-kids |

The pattern is clear: the universal levers are the **reward-uncertainty family** (variable-ratio / intermittent reward) and the **loss-aversion / investment family** (loss aversion, endowment, sunk cost, streaks, goal-gradient, endowed progress, IKEA). These appear everywhere precisely because they exploit deep, domain-independent psychology — which is also why most are flagged Borderline-or-worse.

> Note on `domains_seen`: it records the source-domain provenance of each merged pillar (which research files described that mechanic), not every product that uses it. Several pillars common in practice across many domains (e.g. mascots, achievements) carry fewer tags because they were only *explicitly catalogued* in a couple of source files. Treat 4+ as a strong-signal floor, not an exhaustive usage map.

## Dark-pattern summary

`dark_pattern` flag distribution (by leading token, collapsing the parenthetical qualifiers):

- **No** (incl. "No (mostly)", "No (structural)", "No (applied form)"): ~156
- **Borderline** (incl. "Borderline to Yes", "Borderline (mostly pro-user)", "Caution", "Mixed"): ~74
- **Yes** (incl. all "Yes (...)" qualifiers): **66**

### Pillars flagged Yes (manipulative / compulsion-engineering)

**Foundational mechanisms that are dark when weaponized (Category 1):** P002 Variable-Ratio Reinforcement · P005 Variable-Interval (Compulsive Checking) · P006 Negative Reinforcement · P007 Conditioned Cues · P008 Wanting-vs-Liking · P009 Dopamine Prediction Error · P010 Dopamine "Maybe" · P012 The Hook Model · P019 Black-Hat Drives · P024 Loss Aversion · P025 Endowment Effect · P026 Sunk-Cost · P029 Near-Miss · P035 Default/Status-Quo Bias · P036 Present Bias · P037 Curiosity/Information-Gap · P038 Cialdini's Principles.

**Reward / monetization (Cats 3, 6, 8):** P074 Big-Win Seeding · P076 Bonus Rounds/Free Spins · P109 Sunk-Cost & Endowment Binding · P110 Progressive Jackpots · P146 Vicarious Reinforcement/Jackpot Advertising · P160 Comps/VIP Binding.

**Social / parasocial (Cats 7, 12, 11):** P130 Friend Streaks · P174 Anonymity & Disinhibition (double-edged) · P176 Parasocial Attachment · P180 AI-Companion Bonding · P183 AI Companionship for the Lonely · P184 Relationship Investment Loop.

**Friction / triggers (Cats 14, 15):** P203 One-Tap (for spending) · P234 Notification/Red-Badge Engineering · P237 Guilt-Trip Notifications · P238 Reverse-Psychology Notification.

**Compulsion Engineering & Dark Patterns (Cat 17 — primarily manipulative):** P258 Infinite Scroll · P259 Pull-to-Refresh Slot Machine · P260 Autoplay/Seamless Next · P261 The Machine Zone · P262 Losses Disguised as Wins · P263 Sensory Reinforcement Calibrated to Addict · P264 Rapid Play Rate · P265 Illusion of Control · P266 Partial-Reinforcement Extinction Effect · P267 Loot Boxes & Gacha · P268 Gacha Pity & FOMO Banners · P269 Blind-Box/Gacha Toys (Kids) · P270 Energy/Lives/Stamina Gates · P271 Hearts & Cost of Mistakes · P272 Dual Currencies/Price Obfuscation · P273 Whale Monetization · P275 Chasing Losses · P276 Gambler's/Hot-Hand Fallacy Framing · P277 Almost-Won Tease Messaging · P278 Scratchcards/Daily-Spin Wheels · P279 Social Casino Apps · P280 Multiline/Constant Reinforcement · P281 Bet-Size Escalation · P282 Reverse Withdrawal · P283 Friction Asymmetry (Roach Motel/Forced Continuity) · P284 Confirmshaming/Sneaking · P285 Default-Public/Obstructive Privacy · P286 Absence-of-Validation as Social Pain · P287 Social-Validation Slot Machine · P289 Outrage/Rage-Bait Amplification · P290 Comment-Bait · P292 Social-Comparison Harm · P295 Emotional-Manipulation Dark Patterns.

(66 total flagged Yes; ~74 more are Borderline/Caution and must be used with user-protective guardrails. The ethical north star across the catalog is **P014 Self-Determination Theory** — does the mechanic serve a goal the user themselves holds, or manufacture a need only the product can relieve?)

## Notable merges & splitting decisions

- **Streaks were deliberately split into four pillars**, not one: P044 *Daily Streaks* (the core counter), P045 *Streak Freeze / Forgiveness & Repair* (a genuinely distinct design lever — slack increases persistence), P046 *Streak Milestones & Identity Recognition*, P047 *Don't-Break-the-Chain Visualization*, and P130 *Friend Streaks* (the social/relationship variant, which carries a much harsher dark-pattern flag). The design levers differ enough to keep them apart.
- **Variable reward appears as five related-but-distinct rows** spanning three meta-categories: P002 (the *principle*, in Behavioral Theory), P070 (*applied* loot/chest rewards), P071 (*ethically-bounded* wellness variant), P194 (*variable reward of novelty* in feeds), and P259/P279 (the *slot-machine* compulsion forms in Cat 17). The brief explicitly asked for the principle vs applied vs dark-pattern forms to live in different categories.
- **Near-miss** kept as both P029 (the *cognitive principle*, Cat 1) and P277 (*Almost-Won tease messaging*, the verbal/UI compulsion layer in Cat 17).
- **Loss aversion + sunk cost + endowment + IKEA + endowed-progress** were kept as separate cognitive-bias pillars (P024–P028, P034) rather than merged into one "loss family," because each is a distinct, separately-citable lever, and several reappear as *applied* pillars in Cats 6/14/17.
- **Game feel / juice** split into P061 (the *disproportionate-feedback* juice concept) and P062 (*responsive real-time control*, Swink) — different craft levers.
- **SDT appears twice by design**: P014 (the macro-framework in Behavioral Theory) and is the stated north star; the fitness file's restatement was folded into P014 rather than duplicated.
- **Parasocial / mascot / companion** was spread across the right homes: P175/P186 (mascots as brand attachment vs delight), P176 (the general parasocial principle), P177/P178 (virtual-pet nurturing), P179 (voice coaching), and P180–P184 (the AI-companion cluster with its heavy dark-pattern flags).
- **Commitment devices, implementation intentions, habit anchoring, fresh-start** appeared in 2–3 files each and were merged to a single canonical row apiece with `domains_seen` recording the overlap.
- **Friction-reduction items** (the 09 file) were largely kept 1:1 because each maps to a distinct Fogg simplicity factor; only the dark-side pillars (37–38) were grouped under Cat 17 (P283/P284) and the wellness "guilt-free / forgiving" items were merged with the meditation file's equivalents (P225/P226).
