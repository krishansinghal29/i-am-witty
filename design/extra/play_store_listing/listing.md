# Riffy — Google Play "Main store listing" (publishable content)

Everything in this folder is what we intend to submit to the Play Store listing.
Copy/paste the text below into Play Console → **Main store listing**, and upload the
images from this folder. All copy is drawn from Riffy's own positioning (landing page),
kept store-appropriate (no explicit content — the app is 18+ but the *listing* must stay clean).

**Last updated:** 2026-06-12

---

## App name (max 30 chars)
```
Riffy
```

## Short description (max 80 chars) — 74 chars
```
A little gym for your social spark. Quick voice reps to sharpen your wit.
```

## Full description (max 4000 chars)
```
Riffy is a little gym for your social spark — a playful way to get quicker, funnier, and more at ease in conversation, one tiny rep at a time.

We all know the feeling: the perfect thing to say shows up an hour too late. Riffy helps you train that muscle so it shows up when it actually counts. Instead of scripts to memorise, you get short, spoken improv reps that build real-time wit and confidence.

HOW IT WORKS
Every rep is three calm beats:
• Read — take in a quick prompt or moment
• Respond — riff your answer out loud (you speak, not type)
• Reflect — get warm, specific feedback on what landed, plus one thing to try next

Reps take about two minutes. The whole idea is to react, not rehearse.

WHAT YOU'LL PRACTISE
A rotating mix of bite-sized exercises that stretch different conversational muscles — playful misinterpretation, quick comebacks, teasing and banter, "yes-and" improv, storytelling sparks and more. Some are wholesome, some are cheeky — it's grown-up, lighthearted fun.

WHY IT WORKS
• Speak your answers — practise out loud, the way real conversation happens
• Two-minute reps — easy to fit into a coffee break
• Gentle daily streaks — show up a little, keep the spark warm
• Warm feedback — encouraging and specific, never harsh

Riffy is built to lower the stakes through play. No audience, no pressure — just you, a few quick reps, and a friendlier, faster version of your own voice.

Made for adults who want to feel sharper and more spontaneous in everyday conversation.
```

---

## Category & contact details (Play Console → "Select an app category and provide contact details")

| Field | Value | Notes |
|---|---|---|
| App category | **Lifestyle** | Self-improvement / social-skills practice. Alt: Education. Changeable later. |
| Tags | (optional) leave for now | Play suggests tags; can add "self improvement", "communication". |
| Contact email | **support@riffy.pro** | Working alias on the riffy.pro Google Workspace. Public on the listing. |
| Contact phone | (leave blank — optional) | |
| Contact website | **https://riffy.pro** | Live. |
| External marketing | leave default | |

---

## Graphic assets (upload from this folder)

| Asset | File | Spec | Status |
|---|---|---|---|
| App icon | `icon-512.png` | 512×512 PNG, 32-bit | ✅ ready |
| Feature graphic | `feature-graphic-1024x500.png` | 1024×500 PNG/JPG | ✅ ready |
| Phone screenshots | `screenshots/01..06-*.png` | 6 images, 1120×1760 (ratio 0.636, valid portrait) | ✅ ready |

### Screenshots — final set (upload in this order)
Source: the real product mockups in `ux_existing/mockups/images/` (1120×1880), cropped to
1120×1760 to remove the dev-note footer strip (it carried the old "i-am-witty" name). These are
the genuine app screens, store-safe (none show the suggestive `sex_with_me` /
`sexual_misinterpretation` exercises — Google rejects sexual content in store screenshots even
when the app is rated for it).

1. `01-home.png` — Today's plan (daily reps)
2. `02-exercise-misinterpretation.png` — exercise in progress: Read → Respond (mic) → Reflect
3. `03-exercise-tease.png` — Question-Answer Tease dialogue exercise
4. `04-exercise-pushpull.png` — scaffolded Push/Pull exercise
5. `05-practice-library.png` — the full exercise library
6. `06-onboarding.png` — "Where do you want to feel quicker?" personalisation

**Skipped (stale branding inside the screen):** `profile.png` and `paywall.png` from the mockups
both show **"Witty+"** (old name) and the paywall shows old pricing ($5.99/mo · $39.99/yr, vs
actual riffy_plus). To use either, edit the source HTML in `ux_existing/mockups/html/`
(`profile.html`, `paywall.html`) — replace "Witty+" → "Riffy+", fix pricing — and re-render.
