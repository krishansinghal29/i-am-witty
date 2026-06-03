# i-am-witty — UX & Visual Design

AI-assisted practice app for **humour, communication, storytelling, and confidence**.
This folder holds **mockups** + this one **visual brief** — the rules for choosing
illustrations, colors, type, and screen layout.

## Who we design for (drives every visual choice)
An **anxious introvert** — afraid of being judged. So visuals must feel **safe, private, and
playful** — *never* clinical, corporate, childish, or like they're grading you.

## Theme: "Cozy Dark Arcade"
Dark-first, gamified, warm. **Calm to plan & record, loud to celebrate.** Energy points at the
user's *progress*, never their *judgment*.

## Color palette
| Token | Hex | Use |
|-------|-----|-----|
| bg | `#150F1E` | page (warm plum-black — never pure black or white) |
| surface | `#221934` | cards |
| surface-2 | `#2A1F40` | raised / sheets |
| text | `#F4EEFB` | primary text |
| muted | `#A99CC0` | secondary text |
| faint | `#6E6385` | hints, inactive |
| line | `rgba(255,255,255,.08)` | borders |
| **purple** | `#9D7BFF` | **primary accent**, active states |
| lime | `#B6F250` | success / completed |
| coral | `#FF7361` | warmth / notifications |
| gold | `#FFB23E` | streak 🔥 |
| ice | `#5CC8FF` | freeze ❄️ (forgiving streak) |

Accents are loud on dark — use them on **wins and celebration**, sparingly elsewhere.

## Typography
- **Display / headings / numbers:** Fredoka (rounded, friendly, confident)
- **Body:** Hanken Grotesk (clean, warm, legible)
- Never Inter / Roboto / Arial / system defaults.

## Choosing illustrations & icons
**Feel:** warm, rounded, expressive, slightly chunky — a friendly companion *cheering you on*.
Think soft 3D or flat-with-soft-shadow characters (Duolingo-warm), open body language, kind faces.

**Do:** sit illustrations on tinted accent "chips" (purple/lime/coral/ice at low alpha) · keep
shapes rounded · saturated but readable on dark · one encouraging hype-friend character voice.

**Don't:** stock-corporate flat people · cold/sharp/clinical shapes · anything implying
surveillance or grading · babyish/kiddie cuteness · harsh red "error" imagery.

**Per activity** use a consistent emoji/illustration + tint: Practice 🎭 purple · Sprint ⚡ lime ·
Radio 🎙️ coral · Breath 🌬️ ice.

**Icons:** rounded line icons, ~2px stroke, consistent weight. Emoji are fine as friendly thumbnails.

## Visual UX rules
- **One clear next step** — highlight a single "Next" card; keep choice/pressure low.
- **Calm planning & recording** — no confetti while the user is being vulnerable.
- **Loud celebration** — confetti, glow, sound only on wins (completing, finishing a round).
- **Evaluate gently** — no big red scores; show progress as XP / level vs. their past self.
- **Show safety** — "private", "no one's listening", forgiving streaks (freeze), no leaderboards.

## Implementation (Ionic React)
The mockups are **static HTML/CSS** for design only. Production screens are built with
**Ionic React** (`@ionic/react`) — keep the "Cozy Dark Arcade" look by overriding Ionic's
CSS variables with the tokens above, not by restyling from scratch.

**Map mockup primitives → Ionic components:**
| Mockup element | Ionic React component |
|----------------|-----------------------|
| `.screen` shell | `IonApp` → `IonPage` (phone frame is mockup-only chrome) |
| `<main class="content">` | `IonContent` (scroll lives here) |
| `<nav class="tabs">` | `IonTabs` + `IonTabBar` / `IonTabButton` (+ `IonRouterOutlet`) |
| chat `.sheet` + `.scrim` | `IonModal` with `breakpoints` (sheet style) |
| `.card` rows | `IonCard` / `IonItem`, custom-styled |
| `.chat-btn`, `.send` | `IonButton` |
| `<textarea>` | `IonTextarea` |
| inline `<svg>` icons | `IonIcon` (rounded line icons, ~2px stroke) |

Theme via Ionic CSS variables (e.g. `--ion-background-color: #150F1E`, `--ion-text-color: #F4EEFB`)
plus the custom tokens; keep Fredoka/Hanken Grotesk as the display/body fonts.

## Mockups
| Screen | Files |
|--------|-------|
| Onboarding *(flow)* | [`mockups/onboarding.html`](mockups/onboarding.html) · [`mockups/onboarding.png`](mockups/onboarding.png) |
| Home | [`mockups/home.html`](mockups/home.html) · [`mockups/home.png`](mockups/home.png) |
| Practice | [`mockups/practice.html`](mockups/practice.html) · [`mockups/practice.png`](mockups/practice.png) |
| Profile | [`mockups/profile.html`](mockups/profile.html) · [`mockups/profile.png`](mockups/profile.png) |
| Witty+ paywall | [`mockups/paywall.html`](mockups/paywall.html) · [`mockups/paywall.png`](mockups/paywall.png) |

Bottom tabs (left→right): **Home · Practice · Role play** *(soon)* **· Profile.** A Telegram-community
button sits just left of the persistent "Chat with us" bubble (top-right, on every screen).

**Practice** is a calm, low-pressure *library* of the common exercises ("Your regulars" + "Fresh
picks", filterable by activity family) you return to any time — distinct from Home's curated daily
path. **Profile** frames progress against *your past self* (level/XP, gentle badges, weekly recap) —
no leaderboards — plus private-by-default settings.

**Onboarding** is an interactive *flow* in one file (`onboarding.html`) — tap an option / "Done" to
walk through all six steps: (1) one emotional trigger question → (2) a single tiny practice *tuned to
that pick* (calm — no confetti while vulnerable) → (3) a variable reward (loud — style label + sharper
rewrite + tiny insight + first-step badge) → (4) login *after* the win ("Save your Day 1 streak?",
Apple/Google/Not now) → (5) a reminder time, after which the OS notification prompt fires → (6) land on
Today's Plan. **No login before the first practice; one question before action.** The PNG captures
step 1; preview any stage in a browser with a hash, e.g. `onboarding.html#3` or `onboarding.html#5perm`.

## Subscriptions (RevenueCat → "Witty+")
Paywall lives in `paywall.html` as a bottom **sheet** (→ Ionic `IonModal`, sheet style). Two triggers,
one shared sheet:
1. **Limit reached** — when the daily free practices run out (the `paywall.html` mockup shows this:
   a gentle "🎯 that's your 3 free practices today — your streak's safe" banner; *not* punishing).
2. **Profile entry points** — a gold/purple **"Go unlimited with Witty+"** card + a **Witty+
   subscription · Free plan** settings row, both opening the same sheet (wired in `profile.html`).

Keep it on-brand for Maya: value-first, no dark patterns, always an easy *"Maybe later"*. The sheet
presents a RevenueCat **Offering** as two **packages** — **Annual** (`$rc_annual`, pre-selected, "Best
value · save 44%") and **Monthly** (`$rc_monthly`) — plus a free-trial line, a **Restore** link, and
Terms/Privacy. Prices/copy are placeholders; production should render live packages from RevenueCat's
`Offerings` and call `purchasePackage` / `restorePurchases`. Gate access on the `"Witty+"`
entitlement.

Open the `.html` in any browser (static preview — **not** the Ionic React build). Regenerate the
PNGs (one per screen):
```bash
for p in onboarding home practice profile paywall; do
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
    --force-device-scale-factor=2 --window-size=440,940 --virtual-time-budget=3500 \
    --screenshot="mockups/$p.png" "file://$PWD/mockups/$p.html"
done
```
