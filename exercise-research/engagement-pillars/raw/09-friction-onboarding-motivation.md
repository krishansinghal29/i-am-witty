# Friction-Reduction, Onboarding, Activation & Low-Effort Re-Engagement — The "Requires Less Motivation" Playbook

**Total pillars cataloged: 38**

## Framing

BJ Fogg's behavior model says **Behavior = Motivation × Ability × Prompt (B=MAP)**. The three must converge in the same moment. The central, counter-intuitive insight: when motivation is low (which it usually is), the durable win is to raise **Ability** — make the behavior easier — and to **time the Prompt** well. Motivation is volatile and expensive to manufacture; simplicity is stable and compounding. Fogg defines ability as simplicity along six factors — **Time, Money, Physical Effort, Brain Cycles (mental effort), Social Deviance, Non-Routine** — and notes the "simplicity chain" is only as strong as its weakest link: the scarcest factor for a given user is the one that actually gates the behavior. This document catalogs the mechanics that lower activation energy across onboarding, in-product friction, prompts/triggers, and re-engagement — and flags where friction-removal curdles into manipulation (dark patterns), especially **friction asymmetry** (easy in, hard out).

Sources for framing: https://www.behaviormodel.org/ · https://www.triplewhale.com/blog/fogg-behavior-model · https://yukaichou.com/behavioral-analysis/bj-fogg-extended-part-1-of-2/

---

### 1. Minimize Time-to-Value / Fastest Path to First "Aha"
- **Category:** onboarding / activation
- **Definition:** Compress the distance between first open and the moment a user first experiences the product's core value, removing every step that doesn't directly serve that first payoff.
- **Why it works (psychology):** Fogg's Time + Brain-Cycles factors — the longer and more effortful the path, the lower the ability, so fewer convert. Time-to-value (TTV) is empirically predictive of retention: users who reach value within 24 hours retain dramatically better at 30/60/90 days than those who take days. Early value also exploits the peak of post-install motivation before it decays.
- **Product examples:** Slack (you've sent your first message in seconds); Loom (record and share a video before any account setup); Canva (a usable design appears in under a minute); Superhuman's famously fast inbox triage.
- **How to apply:** Define your single "aha" event (a behavior statistically tied to retention), then ruthlessly cut steps before it. Measure median TTV and treat shortening it as a primary growth lever. Defer everything optional (profile, settings, invites) until after the first win.
- **Dark pattern?:** No.
- **Sources:** https://amplitude.com/blog/aha-moment · https://amplitude.com/blog/time-to-value-drives-user-retention · https://www.lennysnewsletter.com/p/what-is-a-good-activation-rate

### 2. Instant Onboarding / Defer the Signup Wall (Try Before You Register)
- **Category:** onboarding / friction
- **Definition:** Let users experience the product (or a meaningful slice of it) before forcing account creation; move the registration wall to after the first value, not before it.
- **Why it works (psychology):** The signup wall is a Time + Brain-Cycles + Money(perceived-commitment) tax levied before any value is demonstrated, so motivation is at its lowest exactly when effort is demanded. Deferring it lets the value itself supply the motivation to register.
- **Product examples:** Figma and Canva (explore/edit before paywall — "reverse trial" model); ChatGPT and many tools allowing a query before login; ASOS moved account creation to *after* purchase and lifted conversion ~50%.
- **How to apply:** Ask: "What's the smallest valuable thing a user can do with zero account?" Let them do that. Capture the account only when there's something worth saving (their work, their result, their progress). Use a "reverse trial": full value first, gate later.
- **Dark pattern?:** No.
- **Sources:** https://katyarozhko.substack.com/p/try-before-you-buy-the-reverse-trial · https://baymard.com/learn/checkout-flow-ux-optimization · https://www.news.aakashg.com/p/plg-in-2026

### 3. Guest Checkout / No-Account-Required Completion
- **Category:** friction / onboarding
- **Definition:** Allow users to complete the primary transaction (buy, book, submit) without creating an account, offering optional account creation afterward.
- **Why it works (psychology):** Forced account creation is one of the top documented abandonment causes — Baymard finds ~26–37% of checkout abandoners cite mandatory account creation. It adds Time + Brain-Cycles (another password to invent and remember) with no perceived benefit at the decision moment.
- **Product examples:** Amazon-style express purchase; most modern e-commerce (ASOS post-purchase account = +50% conversion); Apple Pay / one-time guest pay flows.
- **How to apply:** Make guest checkout the prominent, equal-or-default option (half of sites hide it). Offer "create an account" as a one-click post-purchase step pre-filled with the data already entered.
- **Dark pattern?:** No. (But note: hiding the guest option to coerce sign-up is a mild dark pattern.)
- **Sources:** https://www.nofraud.com/blog/the-importance-of-guest-checkout/ · https://baymard.com/learn/checkout-flow-ux-optimization

### 4. Passwordless / Social / One-Tap Login
- **Category:** friction / onboarding
- **Definition:** Replace password creation and entry with magic links, OTPs, passkeys, social OAuth, or one-tap identity providers.
- **Why it works (psychology):** Password creation is a Brain-Cycles + Time tax and a major failure point — Calendly found 67% of registration abandonments happened at password creation; moving to magic links lifted completion from 43% to 71%. Google One Tap has driven reported +90% signups and +100% mobile sign-ins. Removes the "forgot password" re-entry friction entirely.
- **Product examples:** Slack and Notion (magic links); "Continue with Google/Apple" everywhere; Google One Tap; passkeys on modern OSes.
- **How to apply:** Offer 1–2 social providers plus a magic-link/OTP fallback. Avoid presenting a forest of provider buttons (Hick's law). Remember the last-used method to make return logins one tap.
- **Dark pattern?:** No. (Watch: social login can over-harvest data/permissions — request the minimum scope.)
- **Sources:** https://guptadeepak.com/the-complete-guide-to-google-one-tap-login-everything-developers-need-to-know/ · https://www.loginradius.com/blog/identity/passwordless-magic-links

### 5. Progressive Onboarding & Progressive Disclosure
- **Category:** onboarding / friction
- **Definition:** Reveal features and information gradually as the user is ready for them, rather than front-loading everything; teach in context, just-in-time.
- **Why it works (psychology):** Coined by Jakob Nielsen (1995). Directly lowers Brain-Cycles by keeping the interface and the mental model small at any one moment, preventing overwhelm and reducing errors. Respects working-memory limits (Miller's ~7±2).
- **Product examples:** Slack and Duolingo (minimal first UI, features surface over time); Notion (core editor first, databases later); accordion/tab UIs and tooltips that defer detail.
- **How to apply:** Show only what's needed for the current step; put advanced options behind "more" / secondary screens. Use in-context tooltips at the moment of first relevance rather than an upfront tour. Sequence feature introductions to behavior milestones.
- **Dark pattern?:** No.
- **Sources:** https://www.nngroup.com/articles/progressive-disclosure/ · https://www.uxpin.com/studio/blog/what-is-progressive-disclosure/ · https://ixdf.org/literature/topics/progressive-disclosure

### 6. Smart Defaults & Pre-Filled Choices (The Default Effect)
- **Category:** friction / onboarding
- **Definition:** Pre-select the choice most users would want, and pre-fill known fields, so the path of least resistance is also the right one.
- **Why it works (psychology):** The default effect (Thaler & Sunstein, choice architecture) — a meta-analyzed effect size around d≈.68. Defaults reduce Brain-Cycles, exploit status-quo bias and inertia, and are read as an implicit recommendation. Doing nothing is easier than choosing, so the default usually wins.
- **Product examples:** Organ-donation opt-out countries; 401(k) auto-enrollment ("Save More Tomorrow"); Gmail's "smart" suggested settings; e-commerce pre-selecting standard shipping; pre-filled address from prior data.
- **How to apply:** Set defaults to the genuinely best/most-common choice for the user (not for you). Pre-fill anything you already know. Always allow easy override.
- **Dark pattern?:** No — *unless* defaults serve the company against the user (pre-checked add-ons, pre-opted-in marketing/data sharing). That flips to a dark pattern ("sneak into basket," forced opt-in). Defaults must benefit the user.
- **Sources:** https://www.behavioraleconomics.com/resources/mini-encyclopedia-of-be/nudge/ · https://yukaichou.com/behavioral-analysis/nudge-theory-thaler-sunstein-choice-architecture/

### 7. One-Tap / Single-Action Design
- **Category:** friction
- **Definition:** Collapse a desired action into a single tap/click, eliminating intermediate confirmation and configuration steps.
- **Why it works (psychology):** Minimizes Physical Effort and Time to near-zero, so even very low motivation suffices. Each removed step removes a drop-off point.
- **Product examples:** Amazon "Buy Now" / 1-Click; Apple Pay double-click; Tinder swipe; Instagram double-tap like; Duolingo's single-tap lesson start.
- **How to apply:** For high-frequency core actions, design a single-gesture path. Reserve confirmation only for destructive/irreversible/high-cost actions.
- **Dark pattern?:** No for benign actions — **Yes** when one-tap removes deliberation from spending money (Amazon 1-Click purchases, one-tap in-app purchases, one-tap "upgrade") so users buy before they think. The asymmetry (one tap to buy, many to refund) is the tell.
- **Sources:** https://www.nngroup.com/articles/ten-usability-heuristics/ · https://www.uxpin.com/studio/blog/dark-patterns-in-ux-design/

### 8. Reduce Choice & Options (Hick's Law / Paradox of Choice)
- **Category:** friction
- **Definition:** Cut the number of options presented at any decision point; curate rather than enumerate.
- **Why it works (psychology):** Hick's Law (Hick & Hyman): decision time grows logarithmically with the number of options. The Paradox of Choice (Schwartz): too many options cause paralysis, lower satisfaction, and abandonment. Fewer choices = lower Brain-Cycles.
- **Product examples:** Apple's deliberately small product lines; Google's single search box; Headspace limiting onboarding paths to ~6; streaming "Top Picks" rows instead of the full catalog.
- **How to apply:** Per screen/task, aim for one primary decision. Group, hide, or stage secondary options. Use sensible defaults to make "no decision" viable. Curate down rather than expecting users to filter up.
- **Dark pattern?:** No.
- **Sources:** https://lawsofux.com/hicks-law/ · https://www.dynamiclayer.io/news/the-paradox-of-choice · https://thedecisionlab.com/reference-guide/design/hicks-law

### 9. Always Show One Clear Next Action / Eliminate Dead Ends
- **Category:** onboarding / friction
- **Definition:** At every screen there is one obvious, prioritized next step; no screen leaves the user stranded with nothing to do.
- **Why it works (psychology):** A single, visually dominant CTA removes the Brain-Cycles of figuring out "what now." Multiple competing primary CTAs cause hesitation and bounce ("five buttons → they go nowhere"). Continuous momentum keeps the user in flow.
- **Product examples:** Linear/Notion empty states that suggest the next action; checkout flows with one prominent "Continue"; onboarding checklists that always highlight the next item.
- **How to apply:** One primary CTA per view; at most one differentiated secondary. Design every empty state and end-of-flow to propose the next step. Repeat the same CTA where users may be ready at different scroll points.
- **Dark pattern?:** No.
- **Sources:** https://uxmag.com/articles/usability-tip-one-main-call-to-action-item-per-task · https://courseux.com/call-to-action-ux/

### 10. Reduce Cognitive Load ("Don't Make Me Think")
- **Category:** friction
- **Definition:** Make interfaces self-evident so users understand what to do without conscious effort; trim anything that makes them pause.
- **Why it works (psychology):** Steve Krug's First Law of Usability. Users scan, satisfice, and muddle through — they don't read carefully or optimize. Self-evident design minimizes Brain-Cycles, the most commonly scarce simplicity factor for engaged-but-low-motivation users.
- **Product examples:** Google's near-empty homepage; Stripe's clean checkout; Apple's plain-language settings; clear, conventional navigation labels over clever names.
- **How to apply:** Use conventions, clear labels, and visual hierarchy. Ruthlessly trim words and elements. Test with the "trunk test" (a user dropped on any page should know where they are and what to do). Prefer recognition over recall.
- **Dark pattern?:** No.
- **Sources:** https://www.nngroup.com/articles/minimize-cognitive-load/ · https://readingraphics.com/book-summary-dont-make-me-think/

### 11. Autosave & Forgiveness (Undo, No Lost Progress)
- **Category:** friction
- **Definition:** Continuously save state and make actions reversible (undo/redo, trash, version history) so mistakes and interruptions never destroy work.
- **Why it works (psychology):** Maps to Nielsen heuristics "User Control & Freedom" and "Error Prevention." Removes the fear-tax that makes users hesitate; lowers Brain-Cycles (no need to remember to save) and the emotional cost of mistakes. Fear of loss is a powerful inhibitor — removing it raises ability.
- **Product examples:** Google Docs (autosave + version history); Figma (real-time autosave, undo stack); Gmail "Undo Send"; macOS trash; Notion page history.
- **How to apply:** Autosave by default; never rely on an explicit save. Provide generous undo and a recoverable trash. Prefer a recoverable action plus undo over a blocking confirmation dialog.
- **Dark pattern?:** No.
- **Sources:** https://www.nngroup.com/articles/user-control-and-freedom/ · https://www.nngroup.com/articles/ten-usability-heuristics/

### 12. Frictionless Re-Entry / Resume Where You Left Off
- **Category:** re-engagement / friction
- **Definition:** When a user returns, drop them exactly where they stopped — same content, same position, same context — across sessions and devices.
- **Why it works (psychology):** Re-entry has its own activation energy; resuming removes the Time + Brain-Cycles of re-orienting and re-navigating. It also exploits the Zeigarnik effect (unfinished tasks nag), pulling users back to complete what they started.
- **Product examples:** Netflix "Continue Watching" with cross-device timestamp sync; Kindle Whispersync page position; Spotify resuming a podcast mid-episode; mobile games reopening to the last screen.
- **How to apply:** Persist session state server-side and sync across devices. Surface a prominent "continue" entry point on return. Avoid re-showing onboarding or re-asking for context already captured.
- **Dark pattern?:** No.
- **Sources:** https://medium.com/@kanishks772/the-real-secret-sauce-behind-netflixs-seamless-resume-experience-f8de30d9c453

### 13. Streak Insurance / Streak Freeze (Lower the Stakes of Breaking a Habit)
- **Category:** re-engagement / friction
- **Definition:** Let users protect a streak through an unavoidable miss (a "freeze," "repair," or grace day) so one bad day doesn't erase accumulated progress.
- **Why it works (psychology):** Penn/UCLA research shows giving people a little "slack" toward goals is *more* motivating than rigid rules — it prevents the "what-the-hell effect" where one miss triggers total abandonment. Removes the all-or-nothing fragility that makes streaks brittle and shame-inducing.
- **Product examples:** Duolingo Streak Freeze (equip up to two; doubling availability raised daily active learners +0.38%) and Streak Repair; Snapchat streak-restore; many fitness apps' "rest day doesn't break the streak."
- **How to apply:** Build in automatic or cheap grace days. Auto-apply protection on a miss rather than punishing. Communicate forgivingly ("Your streak is safe") to reduce abandonment spirals.
- **Dark pattern?:** Mostly No — but streaks can become coercive (anxiety, FOMO-driven compulsion). **Caution:** selling streak repairs for money, or weaponizing streak-loss dread, edges toward manipulation. Keep protection cheap/free and the framing kind.
- **Sources:** https://blog.duolingo.com/how-duolingo-streak-builds-habit · https://duoplanet.com/duolingo-streak-freeze/

### 14. Guilt-Free, No-Shame Design
- **Category:** re-engagement / prompts
- **Definition:** Frame absence, lapses, and partial completion with warmth and zero blame; welcome users back instead of scolding them.
- **Why it works (psychology):** Shame raises the emotional cost (a Brain-Cycles/Social-Deviance tax) of returning and triggers avoidance — people skip the app to avoid feeling judged. Self-compassion research shows kindness after lapses improves recovery and persistence more than guilt.
- **Product examples:** "Welcome back, let's pick up where you left off" framing; Headspace and Calm's gentle, non-judgmental copy; Duolingo's playful-but-not-punishing comeback messaging (vs. its notorious guilt-trip memes — the counter-example).
- **How to apply:** Replace "You broke your streak!" with "Ready to start again?" Avoid red shame-states for missed goals. Make re-entry feel like a soft landing, not a walk of shame.
- **Dark pattern?:** No — and notably the *opposite* of confirmshaming, which is a dark pattern.
- **Sources:** https://www.suebehaviouraldesign.com/en/blog/dark-patterns-explained/ · https://blog.duolingo.com/how-duolingo-streak-builds-habit

### 15. Snackable / Bite-Sized Micro-Sessions ("Just 5 Minutes," "One Lesson")
- **Category:** friction / re-engagement
- **Definition:** Package the core activity into very short, self-contained units that deliver value in a few minutes.
- **Why it works (psychology):** Slashes the Time factor and the perceived commitment; a 5-minute ask clears the bar even on low-motivation days. Aligns with the two-minute rule and the lower activation energy of small first steps. Short units also fit into existing gaps in the day.
- **Product examples:** Duolingo lessons (~3–5 min); TikTok/Reels/Shorts (15–60s units; ~2.5× the engagement of long video); Headspace 3–10 min meditations; Blinkist book summaries; NYT mini-crossword.
- **How to apply:** Define a "minimum valuable session" and make it the default unit. Let users always do "just one." Show realistic, small time estimates ("2 min"). Make stopping after one unit feel complete, not abandoned.
- **Dark pattern?:** No for the format itself — **Caution:** infinite-scroll/autoplay chains of snackable units can become compulsive ("just one more"), which is a separate engagement-trap pattern.
- **Sources:** https://thrivesearch.com/snackable-content-bite-sized-engagement-in-a-time-starved-world/ · https://techcrunch.com/2024/10/07/revyze-a-tiktok-for-education-startup-draws-on-duolingo-to-add-bite-sized-learning-too/

### 16. Reduce Setup Cost & the Blank-Page Problem (Templates, Starter Content)
- **Category:** onboarding / friction
- **Definition:** Replace the empty, intimidating blank state with templates, sample data, or pre-built starter content the user can edit rather than create from scratch.
- **Why it works (psychology):** The blank page is maximal Brain-Cycles + decision paralysis ("blank-page anxiety"). Editing is far cheaper than creating; a template provides scaffolding, a worked example, and an implicit "you're allowed to do it like this."
- **Product examples:** Notion's personalized template gallery (preloads a workspace from onboarding answers, turning hours into minutes); Canva templates; Google Docs/Sheets templates; Webflow/Wix starter sites; spreadsheet sample data.
- **How to apply:** Never ship a raw empty state. Offer 3–5 relevant templates (personalized from onboarding answers when possible). Seed sample/dummy content the user can tweak. Frame as "start here, then make it yours."
- **Dark pattern?:** No.
- **Sources:** https://wyndomb.medium.com/how-notion-solved-the-blank-page-problem-686b2e73ae57 · https://goodux.appcues.com/blog/notions-lightweight-onboarding

### 17. Personalization at Onboarding (Tailored First Experience)
- **Category:** onboarding / activation
- **Definition:** Ask a few targeted questions, then immediately customize the first experience (content, templates, goals) to the answers.
- **Why it works (psychology):** A Headspace study found a short personalization quiz raised course starts by +7.6 pts over a generic default. Two mechanisms: (1) relevance — the first content is already useful, shortening TTV; (2) the IKEA/endowment effect plus "feeling seen" — the act of asking signals listening, and co-created experiences feel like "mine." Must be balanced against the Time cost of the questions.
- **Product examples:** Spotify artist/genre picker → instant personalized playlists; Headspace path self-selection; TikTok's interest-inferring first feed; Duolingo's goal/level questions.
- **How to apply:** Ask the *minimum* questions that materially change the first experience; show value immediately after. Keep it to a few taps. Never collect data you won't use to personalize.
- **Dark pattern?:** No — *unless* the "personalization" survey is a pretext to harvest data or pad perceived effort without delivering tailored value.
- **Sources:** https://www.purchasely.com/blog/headspace-behavioral-science-onboarding-experiment · https://www.appcues.com/blog/user-onboarding-personalization

### 18. Well-Timed Contextual Triggers / Prompts (Right Moment, Not Nagging)
- **Category:** prompts / re-engagement
- **Definition:** Deliver the prompt to act at the moment the user is most able and most likely to want to — aligned to context, routine, or an internal trigger — rather than on a blanket schedule.
- **Why it works (psychology):** In B=MAP the prompt only works if it lands when Motivation and Ability are both present. Nir Eyal: a good trigger is well-timed, actionable, and tied to an internal trigger (boredom, uncertainty). Mistimed prompts get ignored or, worse, train users to dismiss/disable notifications.
- **Product examples:** Calendar reminders before a meeting; Duolingo learning a user's habitual practice time; geofenced retail offers when near a store; "Your ride is 2 min away" delivery updates.
- **How to apply:** Trigger off behavior and context, not just clocks. Learn each user's active window. Make every prompt actionable and relevant; cap frequency; let users tune it. Quality over volume — irrelevant prompts erode the whole channel.
- **Dark pattern?:** No when genuinely helpful — **Yes** when notifications manufacture false urgency, fake social pressure ("X is waiting for you"), or are deliberately frequent to drive compulsive opens. The line is whether the prompt serves the user's goal or only yours.
- **Sources:** https://www.nirandfar.com/notifications-that-work/ · https://medium.com/busuu/designing-push-notifications-that-dont-suck-af6aaa0ea85

### 19. Habit Anchoring to Existing Routines (Habit Stacking)
- **Category:** prompts / re-engagement
- **Definition:** Attach the desired behavior to a stable existing routine so the old habit becomes the reliable cue for the new one.
- **Why it works (psychology):** Fogg's "anchoring" (Tiny Habits) and James Clear's habit stacking: "After [current habit], I will [new behavior]." The existing routine supplies a free, consistent prompt, removing the Non-Routine penalty and the need to remember.
- **Product examples:** Meditation apps prompting "after your morning coffee"; language apps suggesting practice "on your commute"; fitness apps anchoring to "after you brush your teeth"; tying a journaling app to bedtime.
- **How to apply:** Help users pick a concrete, daily anchor and phrase the stack explicitly. Schedule reminders to that anchor moment. Design the action to be doable in the slot the anchor creates.
- **Dark pattern?:** No.
- **Sources:** https://jamesclear.com/habit-stacking · https://en.wikipedia.org/wiki/Implementation_intention

### 20. Implementation Intentions ("When X, I'll Do Y")
- **Category:** prompts / onboarding
- **Definition:** Have users pre-commit to a specific if-then plan specifying when, where, and how they'll perform the behavior.
- **Why it works (psychology):** Gollwitzer (1999): if-then planning makes people 2–3× more likely to follow through by pre-deciding the response to a cued situation, so the behavior fires automatically without in-the-moment deliberation (lower Brain-Cycles, defeats Non-Routine).
- **Product examples:** Fitness/habit apps asking users to set a specific day/time/place; flu-shot reminder studies asking people to write *when* they'll go; goal apps that capture an explicit "I will [X] at [time] in [place]."
- **How to apply:** During onboarding/goal-setting, prompt for the concrete when/where, not just the what. Store it and reflect it back in reminders ("It's 7am — your planned practice time").
- **Dark pattern?:** No.
- **Sources:** https://www.prospectivepsych.org/sites/default/files/pictures/Gollwitzer_Implementation-intentions-1999.pdf · https://en.wikipedia.org/wiki/Implementation_intention

### 21. The Two-Minute Rule / Shrink the First Step
- **Category:** onboarding / friction
- **Definition:** Reduce the entry behavior to a version that takes ~two minutes or less, so showing up is trivially easy.
- **Why it works (psychology):** James Clear's two-minute rule and Fogg's "tiny" / starter steps. The hardest part is starting; a tiny first step lowers activation energy below the motivation floor. Momentum and consistency ("master the art of showing up") matter more early than intensity.
- **Product examples:** "Read one page" / "put on running shoes" gateway habits; Duolingo's one-question start; meditation apps' "just three breaths"; writing apps' "write one sentence."
- **How to apply:** Make the default first action absurdly small. Let "starting" count as success. Expand only after the showing-up habit is stable. Frame the ask as the tiny version, not the full behavior.
- **Dark pattern?:** No.
- **Sources:** https://www.entrepreneur.com/business-news/james-clear-two-minute-rule-is-the-key-to-habit-building/472990 · https://jamesclear.com/habit-stacking

### 22. Endowed-Progress Head Starts
- **Category:** onboarding / activation
- **Definition:** Give users artificial initial progress toward a goal (pre-completed steps, starter points) so they feel closer to completion from the outset.
- **Why it works (psychology):** Nunes & Drèze (2006): a 10-stamp card with 2 free stamps beat an 8-stamp empty card (34% vs 19% completion) despite identical real work. Perceived proximity to a goal increases effort and reduces dropout (goal-gradient effect).
- **Product examples:** LinkedIn "Profile Strength" starting partway full; onboarding checklists with the first item pre-checked (account already created); loyalty programs starting with bonus points; setup wizards showing "Step 1 of 5 ✓ done."
- **How to apply:** Start progress bars above zero by crediting steps already taken (signup, email verify). Frame setup checklists with an early item pre-completed. Make the first milestone feel near.
- **Dark pattern?:** No — *unless* the "progress" is illusory busywork manufactured purely to bait sunk-cost commitment with no real value.
- **Sources:** https://www.coglode.com/nuggets/endowed-progress-effect · https://uxdesign.cc/endowed-progress-effect-give-your-users-a-head-start-97d52d8b0396

### 23. Commitment Devices & Pre-Commitment (Raise Future Ability)
- **Category:** onboarding / prompts
- **Definition:** Let users voluntarily lock in future behavior by pre-arranging constraints, stakes, or automation while motivation is high, so willpower isn't needed later.
- **Why it works (psychology):** Addresses time-inconsistent preferences (present bias): the motivated present-self constrains the lazy future-self. Stakes/automation convert a future high-effort decision into a low-effort default. "Save More Tomorrow" (Thaler & Benartzi) pre-commits raises to savings.
- **Product examples:** stickK (forfeit money/anti-charity stakes); Beeminder (auto-charges if you fall off your data line); 401(k) auto-escalation; scheduled recurring transfers; "schedule send."
- **How to apply:** Offer opt-in pre-commitment at the high-motivation moment (signup, goal-setting): auto-scheduling, recurring actions, optional stakes, lock-ins with a chosen friend/referee. Keep stakes user-chosen and proportionate.
- **Dark pattern?:** No when user-initiated and escapable. **Caution:** company-imposed "commitments" the user can't exit (lock-in contracts, non-cancelable plans) are coercive, not empowering.
- **Sources:** https://en.wikipedia.org/wiki/Commitment_device · https://www.behavioraleconomics.com/resources/mini-encyclopedia-of-be/precommitment/

### 24. Fast Performance / Loading as Engagement
- **Category:** friction
- **Definition:** Treat raw speed (load time, latency, responsiveness) as a first-class engagement feature, because slowness is friction users feel instantly.
- **Why it works (psychology):** Speed is the Time factor at the millisecond level. Google: bounce probability rises ~32% as load goes 1→3s and ~90% by 5s; 53% of mobile users abandon pages over 3s; Walmart saw +2% conversion per 1s improvement. Latency directly suppresses ability to act.
- **Product examples:** Google Search's sub-second results; Amazon's latency-revenue findings; Instagram/TikTok pre-loading the next item; Stripe/Linear's snappy UIs.
- **How to apply:** Budget and monitor Core Web Vitals; optimize the critical path to first value. Pre-fetch likely next content. Make the *first meaningful interaction* fast even if full load isn't.
- **Dark pattern?:** No.
- **Sources:** https://wp-rocket.me/blog/website-load-time-speed-statistics/ · https://www.outerboxdesign.com/articles/cro/page-speed-conversion-statistics/

### 25. Lower *Perceived* Effort (It Looks Quick) — Perceived Performance
- **Category:** friction / onboarding
- **Definition:** Make the experience *feel* fast and easy via skeleton screens, optimistic UI, progress feedback, and honest "takes 2 minutes" framing — independent of literal speed.
- **Why it works (psychology):** Perceived ability gates action as much as actual ability. Skeleton screens feel ~20% faster than spinners for identical waits; progress bars that accelerate feel faster; "60-second signup" framing lowers the perceived Time tax before users even start.
- **Product examples:** Facebook/LinkedIn/YouTube skeleton screens; optimistic UI (the like registers instantly, syncs in background); "Sign up in 60 seconds / No credit card required" labels; multi-step forms showing "Step 2 of 3."
- **How to apply:** Use skeleton screens over spinners; render perceived progress; apply optimistic updates. Label effort honestly but reassuringly. Show short, shrinking step counts.
- **Dark pattern?:** No for honest perceived-speed work — **Caution:** the "labor illusion" (fake progress bars implying work that isn't happening, e.g. bogus "searching 100 sites…") is benevolent at best and deceptive at worst; don't fabricate effort to manipulate.
- **Sources:** https://www.nngroup.com/articles/skeleton-screens/ · https://uxdesign.cc/performance-design-designing-for-the-illusion-of-speed-576110e9e558

### 26. Autofill / Autocomplete / Reduce Typing
- **Category:** friction
- **Definition:** Eliminate manual data entry via browser autofill, address autocomplete, card scanning, contact import, and field inference.
- **Why it works (psychology):** Cuts Physical Effort + Time directly — typing (especially on mobile) is tedious and error-prone. Users abandon forms ~75% less when autofill is used; fill time drops ~35%; address autocomplete cuts entry time up to 78% and errors >20%.
- **Product examples:** Browser/OS autofill (name, email, address, card); Google/Mapbox address autocomplete; Apple Pay/Google Pay populating checkout; card camera scanning; "import contacts."
- **How to apply:** Use correct autocomplete attributes and input types; support OS/browser autofill. Add address autocomplete and card scanning. Pre-fill everything you already know; minimize required fields.
- **Dark pattern?:** No. (Caveat: don't use autofill/import to silently over-collect or spam imported contacts.)
- **Sources:** https://developer.chrome.com/blog/autofill-insights-2024 · https://www.zuko.io/blog/optimizing-the-form-address-field

### 27. Error Prevention Over Error Messages
- **Category:** friction / onboarding
- **Definition:** Design so mistakes can't happen (constraints, sensible formats, inline validation, disabled-until-valid) rather than letting users err and then explaining the error.
- **Why it works (psychology):** Nielsen heuristic "Error Prevention." Preventing errors avoids the frustration, rework, and drop-off that errors cause. Inline validation reduces Brain-Cycles (no guessing the format) and the demoralizing post-submit "everything's wrong" wall.
- **Product examples:** Date pickers (can't type an invalid date); format masks on phone/card fields; inline "username available ✓"; disabling "Submit" until the form is valid; smart constraints on quantity inputs.
- **How to apply:** Constrain inputs to valid values; validate inline as the user types; show requirements upfront (password rules) not after failure. Confirm only truly destructive actions.
- **Dark pattern?:** No.
- **Sources:** https://www.nngroup.com/articles/ten-usability-heuristics/ · https://thedecisionlab.com/reference-guide/design/nielsens-heuristics

### 28. Graceful Failure & Low-Stakes Mistakes
- **Category:** friction
- **Definition:** When something does go wrong, fail softly — preserve user input, explain in plain language, offer a one-tap recovery — so errors are low-cost and non-punishing.
- **Why it works (psychology):** High mistake-cost makes users cautious and hesitant (raising effective effort) and erodes trust. Recoverable, blame-free errors keep users in control and willing to experiment, which is itself a form of friction removal.
- **Product examples:** Forms that retain entries after a failed submit; Gmail "Message not sent — Retry"; offline modes that queue and sync; friendly 404s with a path forward; autosaved drafts surviving a crash.
- **How to apply:** Never wipe user input on error. Write human, non-accusatory error copy with a clear fix. Provide retry/recover. Degrade gracefully offline. Make experimentation safe.
- **Dark pattern?:** No.
- **Sources:** https://www.nngroup.com/articles/ten-usability-heuristics/ · https://www.nngroup.com/articles/user-control-and-freedom/

### 29. Reduce Decision Fatigue (Curated / Auto Picks)
- **Category:** friction / prompts
- **Definition:** Make the decision *for* the user when you can predict it well — auto-curate, auto-recommend, "surprise me," or smart defaults — so they consume rather than choose.
- **Why it works (psychology):** Beyond Hick's law, decision fatigue accumulates across a session; each choice depletes capacity and increases the chance of abandonment or defaulting to "nothing." Auto-picks remove the choosing entirely.
- **Product examples:** Spotify Discover Weekly / Daylist / autoplay radio; Netflix "Play something"; TikTok's algorithmic feed (zero choosing); Amazon "Subscribe & Save" recurring orders; news apps' "For You."
- **How to apply:** Offer a strong default/auto-pick alongside (not instead of) manual choice. Use behavior to curate. Provide a "just pick for me" button. Reserve user choice for where it genuinely adds value.
- **Dark pattern?:** No — **Caution:** algorithmic auto-feeds optimized purely for time-on-app (vs. user benefit) shade into engagement traps; the curation should serve the user's interest.
- **Sources:** https://thedecisionlab.com/reference-guide/design/hicks-law · https://www.dynamiclayer.io/news/the-paradox-of-choice

### 30. Accessibility & Inclusive Design as Friction Removal (Curb-Cut Effect)
- **Category:** friction / onboarding
- **Definition:** Build for the widest range of abilities and contexts (WCAG, captions, large targets, voice, clear language); barriers removed for some users smooth the path for everyone.
- **Why it works (psychology):** The curb-cut effect: features built for disability (captions, voice control, clear layouts, big tap targets) reduce friction universally — for older users, kids, non-native speakers, and anyone in a hard context (noisy room, one hand, bright sun). Lower friction → higher conversion and retention (reported correlations: +retention 88%, +satisfaction 93%).
- **Product examples:** Captions (used by hearing users in silent/loud settings); voice assistants; high-contrast/dark modes; large touch targets; plain-language microcopy; keyboard navigation.
- **How to apply:** Meet WCAG as a floor. Ensure large targets, strong contrast, captions, screen-reader support, plain language, and multiple input modes. Treat accessibility audits as friction audits.
- **Dark pattern?:** No.
- **Sources:** https://reciteme.com/us/news/curb-cut-effect/ · https://www.levelaccess.com/uncategorized/the-curb-cut-effect-how-digital-accessibility-elevates-ux-for-everyone/

### 31. Fresh-Start Effect / Temporal Landmarks for Re-Engagement
- **Category:** re-engagement / prompts
- **Definition:** Time re-engagement and goal prompts to perceived "new beginnings" (Monday, 1st of month, New Year, birthday, post-holiday) when willingness to start fresh peaks.
- **Why it works (psychology):** Dai, Milkman & Riis (2014): temporal landmarks open new "mental accounting periods" that relegate past failures and motivate aspirational behavior. Goal commitments spike — new week +62.9%, new month +23.6%, New Year +145.3%, post-birthday +2.6%.
- **Product examples:** Fitness apps pushing "New Week, New Goals" on Mondays; New-Year resolution campaigns; "It's the 1st — reset your plan"; birthday "fresh start" nudges; back-to-school resets.
- **How to apply:** Schedule re-engagement and goal-setting around landmark dates. Make the landmark salient ("A new week starts tomorrow"). Use it to invite lapsed users back without shame ("Start fresh this Monday").
- **Dark pattern?:** No.
- **Sources:** https://learningloop.io/plays/psychology/fresh-start-effect · https://pubsonline.informs.org/doi/10.1287/mnsc.2014.1901

### 32. Respectful Win-Back / Re-Engagement
- **Category:** re-engagement / prompts
- **Definition:** Bring lapsed users back through personalized, frequency-capped, value-led outreach that respects their attention and addresses why they left.
- **Why it works (psychology):** Reactivating an existing user is cheaper than acquiring a new one, and a well-timed, relevant nudge can re-supply the prompt at a moment ability/motivation have recovered. But over-messaging raises social/annoyance cost and accelerates true churn — so restraint *is* the mechanism.
- **Product examples:** "We miss you" emails (outperform "we want you back"); Duolingo/Headspace comeback nudges; Spotify "Here's what's new" re-engagement; capped 3-email win-back sequences with a meaningful incentive.
- **How to apply:** Segment by churn reason; personalize the offer. Cap frequency (~3 touches). Lead with value/new features, not guilt. Make returning one tap (deep-link straight to value). Honor unsubscribes immediately.
- **Dark pattern?:** No when respectful — **Yes** when win-back becomes relentless spam, manufactured urgency, or hard-to-unsubscribe nagging. Respect for opt-out is the dividing line.
- **Sources:** https://www.braze.com/resources/articles/what-is-a-win-back-campaign-anyway · https://prosperstack.com/blog/winback-campaign/

### 33. Recognition Over Recall / Pre-Populated Context on Return
- **Category:** friction
- **Definition:** Show users their options and prior context rather than making them remember things; surface recent items, saved searches, and history so returning requires no memory work.
- **Why it works (psychology):** Nielsen heuristic "Recognition rather than recall." Recall is high Brain-Cycles; recognition is cheap. Pre-populated recents/history mean a returning user doesn't have to reconstruct where they were or re-find what they used.
- **Product examples:** "Recently opened" files; search history and suggestions; "Buy it again" lists; recently played; pre-filled last-used filters/settings; visible (not hidden) menus.
- **How to apply:** Surface recents, history, and saved state prominently on return. Make options visible rather than requiring memorized commands. Pre-fill last-used selections.
- **Dark pattern?:** No.
- **Sources:** https://www.nngroup.com/articles/ten-usability-heuristics/ · https://thedecisionlab.com/reference-guide/design/nielsens-heuristics

### 34. Forgiving Defaults for Lapses (Auto-Pause, Catch-Up, Adaptive Goals)
- **Category:** re-engagement / friction
- **Definition:** When a user falls behind or goes quiet, the system gently adapts — pausing, lowering the goal, offering catch-up, or auto-resuming — instead of penalizing or piling up backlog.
- **Why it works (psychology):** A mounting backlog (50 unread lessons, a broken plan) is a Brain-Cycles + shame wall that deters return. Adaptive/forgiving defaults keep the next step small and achievable, preventing the "I'm too far behind to bother" abandonment.
- **Product examples:** Podcast apps that don't pile guilt on unplayed episodes; fitness apps that auto-adjust the week's plan after missed days; language apps offering a quick "refresher" instead of the full missed load; "mark all as read" to clear backlog.
- **How to apply:** Don't accumulate punishing backlog. Offer "reset/refresh" and adaptive goals after a lapse. Make the comeback step tiny. Default to forgiveness, not catch-up debt.
- **Dark pattern?:** No.
- **Sources:** https://blog.duolingo.com/how-duolingo-streak-builds-habit · https://www.nngroup.com/articles/user-control-and-freedom/

### 35. Reduce Required Fields / Minimal Data Asks (Progressive Profiling)
- **Category:** onboarding / friction
- **Definition:** Ask for the fewest fields needed to get started; collect additional data progressively over time as it becomes relevant.
- **Why it works (psychology):** Every field is a Time + Physical-Effort + Brain-Cycles cost and a drop-off point; long forms depress completion. Progressive profiling spreads the cost over many low-stakes moments instead of one intimidating wall.
- **Product examples:** Single-field "just your email" signups; Typeform's one-question-per-screen; LinkedIn/Facebook collecting profile details gradually after signup; "complete your profile later" nudges.
- **How to apply:** Cut the signup form to the bare minimum (often just email or a social tap). Ask for the rest later, in context, with clear payoff. One question per screen for unavoidable multi-field flows.
- **Dark pattern?:** No.
- **Sources:** https://www.nngroup.com/articles/4-principles-reduce-cognitive-load/ · https://baymard.com/learn/checkout-flow-ux-optimization

### 36. Onboarding Checklists & Setup Wizards (Sequenced, Endowed Progress)
- **Category:** onboarding / activation
- **Definition:** Break setup into a short, visible checklist or step-by-step wizard with progress indication, guiding users to the activation milestone one easy step at a time.
- **Why it works (psychology):** Chunks a daunting setup into small, low-Brain-Cycles steps (progressive disclosure), provides a clear next action, and leverages goal-gradient + completion drive (Zeigarnik) — an incomplete checklist nags to be finished. Pairs naturally with endowed progress (item 1 pre-checked).
- **Product examples:** Slack/Notion/Asana setup checklists; Shopify's store-setup guide; LinkedIn profile-completion meter; "Getting started" wizards with a progress bar.
- **How to apply:** Keep it to ~3–5 high-value steps ending at activation. Show progress; pre-complete the first step. Make each step one tap where possible. Let users dismiss/return without losing place.
- **Dark pattern?:** No — *unless* the checklist is padded with low-value steps to inflate sunk-cost or push upsells.
- **Sources:** https://goodux.appcues.com/blog/notions-lightweight-onboarding · https://www.coglode.com/nuggets/endowed-progress-effect

### 37. DARK SIDE — Friction Asymmetry: Easy In, Hard Out (Roach Motel / Forced Continuity)
- **Category:** friction (dark pattern)
- **Definition:** Deliberately make starting/subscribing/buying frictionless while making leaving/canceling/refunding maximally difficult — the asymmetry is the manipulation.
- **Why it works (against the user):** Exploits inertia, status-quo bias, and the same effort-aversion that legitimate friction-removal serves — but weaponized. "Roach Motel" hides cancellation (call-to-cancel, desktop-only, buried settings); "Forced Continuity" silently converts a trial into recurring charges. Users stay because leaving costs too much effort, not because they value the product.
- **Product examples (cautionary):** Gym memberships requiring in-person/mail cancellation; "call us to cancel" subscriptions; trials that auto-bill with no reminder; news/SaaS that take one click to subscribe but a maze to cancel.
- **How to apply (the ethical inverse):** Make canceling as easy as subscribing (the FTC "Click-to-Cancel" principle — cancel via the same channel you signed up). Send pre-billing reminders. Offer pause instead of forcing leave. Symmetric friction is the ethical test.
- **Dark pattern?:** **Yes — the canonical one.** Harry Brignull's roach motel + forced continuity; targeted by FTC negative-option rulemaking, GDPR, and consumer-protection law.
- **Sources:** https://blog.mobiversal.com/dark-patterns-or-how-ux-exploits-the-user-roach-motel-and-sneak-into-basket.html · https://www.hklaw.com/en/insights/publications/2024/10/the-new-cancel-culture-the-ftcs-click-to-cancel-rule

### 38. DARK SIDE — Confirmshaming, Sneaking & One-Tap Coercion
- **Category:** friction (dark pattern)
- **Definition:** Friction-removal techniques inverted to manipulate: confirmshaming (guilt-wording the decline option), sneaking pre-checked add-ons into the cart, and one-tap flows engineered to make spending/consent happen before the user reflects.
- **Why it works (against the user):** Borrows the same low-effort defaults, single-action design, and persuasive copy that aid users — but aims them at the company's goal against the user's interest. Pre-checked boxes (default effect misused), shame-worded opt-outs ("No, I don't want to save money"), and frictionless purchase remove the deliberation that would protect the user.
- **Product examples (cautionary):** "No thanks, I like paying full price" decline links; pre-ticked insurance/donation/marketing-consent boxes; one-tap upgrade/upsell with hidden recurring terms; sneak-into-basket add-ons.
- **How to apply (the ethical inverse):** Word decline options neutrally. Never pre-check choices that cost the user money or privacy (opt-in, not opt-out, for anything benefiting you). Add a deliberate confirmation step for spending and irreversible consent. Keep defaults pro-user.
- **Dark pattern?:** **Yes.** Confirmshaming, sneaking, and forced-action are catalogued deceptive patterns (deceptive-design.com / Brignull).
- **Sources:** https://www.uxpin.com/studio/blog/dark-patterns-in-ux-design/ · https://www.suebehaviouraldesign.com/en/blog/dark-patterns-explained/ · https://www.scalablepath.com/ui-ux-design/dark-pattern-examples

---

## Cross-Cutting Notes

- **The simplicity-chain lens:** Before applying any pillar, diagnose *which* of Fogg's six factors (Time, Money, Physical Effort, Brain Cycles, Social Deviance, Non-Routine) is the user's binding constraint. Removing slack on a non-binding factor wastes effort. The catalog maps roughly: Time → items 1,15,24,25,26; Brain Cycles → 5,8,10,29,33; Physical Effort → 7,26; Money/commitment → 2,3; Non-Routine → 19,20,23; Social Deviance/shame → 13,14,34.
- **The ethical test for every friction-removal:** Does the removed friction serve the user's goal or only the company's? Symmetric friction (as easy to leave/undo/cancel as to start/commit/buy) is the cleanest dividing line between empowerment (pillars 1–36) and manipulation (pillars 37–38). Defaults, one-tap, and persuasive copy are neutral tools — direction of benefit determines whether they're friction-removal or dark patterns.
- **Re-engagement ≠ nagging:** Prompts (18, 31, 32) only "require less motivation" when they land at moments of genuine ability/intent. Volume and false urgency convert a helpful prompt into a dark pattern and burn the channel.
