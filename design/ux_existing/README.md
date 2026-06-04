# i-am-witty — UX & Visual Design *(existing / production theme)*

AI-assisted practice app for **humour, communication, storytelling, and confidence**.
This folder mirrors the **shipped app's** look & feel (the `wittifyme` /
`get-game-frontend-react` codebase) — a **light, warm** theme built on **Ionic React**. The screens,
elements, and placements are identical to [`../ux/`](../ux/); only the **visual theme**
differs. Think of `../ux/` as the proposed *"Cozy Dark Arcade"* redesign and this folder
as the *current production* baseline to compare it against.

## Who we design for
An **anxious introvert** practicing in private. The production theme leans **bright, warm,
and friendly** — clean white cards, soft orange warmth, a clear single next step.

## Theme: "Light & Warm" (production)
Light-first, warm, approachable. White surfaces with a soft warm wash, **orange** as the
emotional/celebration accent and **blue** as the primary action / active state. Built on
**Ionic React** (themed via Ionic CSS variables), so it reads as a polished, conventional mobile app.

## Color palette (applied via Ionic CSS variables)
| Token | Hex (≈) | Use |
|-------|---------|-----|
| bg | `#F7F8FA` | page (soft off-white) |
| surface | `#FFFFFF` | cards / sheets |
| text | `#2B2F3A` | primary text (`hsl(222 15% 20%)`) |
| muted | `#6B7589` | secondary text (`hsl(215 16% 50%)`) |
| faint | `#9AA3B2` | hints, inactive |
| line | `#E5EAF1` | borders (`hsl(214 32% 93%)`) |
| tint | `#F8FAFC` | secondary / muted fills |
| **accent** | `#F97316` | **warm accent** — CTAs, gradients, celebration (`hsl(25 95% 53%)`) |
| **primary** | `#3B82F6` | **primary blue** — buttons, links (`hsl(217 91% 60%)`) |
| active | `#0A8FF2` | active tab / selected state (`hsl(210 98% 48%)`) |
| amber | `#F5A30A` | streak 🔥 / "medium" (`hsl(38 92% 50%)`) |
| green | `#16A34A` | success / "easy" (`hsl(142 76% 36%)`) |
| sky | `#0EA5E9` | calm / telegram |
| red | `#EF4444` | destructive / "hard" (`hsl(0 84% 60%)`) |

**Gradients:** warm `linear-gradient(135deg,#F97316,#F7C13B)` (primary CTAs); the active
tab indicator runs blue→orange `linear-gradient(135deg,#0A8FF2,#F97316)`.

**Shadows:** soft & orange-tinted — `0 4px 20px -2px rgba(249,115,22,.10)` (soft),
`0 8px 30px -4px rgba(249,115,22,.20)` (warm).

## Typography
- **All text:** **Inter** (`fontFamily: 'Inter, sans-serif'` in `shared-theme/typography.ts`).
- Headings: Inter 600–700, tight tracking (`-0.25` to `-0.5px`). Body: Inter 400–500.
- *(Note: the proposed redesign in `../ux/` swaps this for Fredoka + Hanken Grotesk.)*

## Icons & imagery
- **Icons:** `IonIcon` line icons (ionicons / `lucide-react`), ~2px stroke, consistent weight.
- **Imagery:** the shipped app uses **real photo personas** (e.g. Anya) for conversation
  practice. These mockups keep the same emoji thumbnails as `../ux/` so the two themes are
  directly comparable element-for-element.

## Visual UX rules (unchanged from `../ux/`)
- **One clear next step** — a single highlighted "Next" card (here in blue, not purple).
- **Calm planning & recording**, **loud celebration** only on wins (confetti).
- **Evaluate gently** — progress vs. your past self, no leaderboards.
- **Show safety** — "private", forgiving streaks.

## Implementation (production stack)
Built with **React + Vite + Capacitor**, **Material UI v6** (`@mui/material`) + a few
**shadcn/Radix** primitives, **Tailwind** tokens (`src/index.css`), **framer-motion** for
motion, **RevenueCat/Superwall** for the paywall. The radius token is `0.75rem` (12px);
these mockups use 12–16px to match.

| Mockup element | Production component |
|----------------|---------------------|
| `.screen` shell | React route under `PageLayout` |
| `<main class="content">` | scrollable page body |
| `<nav class="tabs">` | `BottomNav` (MUI `Paper`, active = blue) |
| chat `.sheet` / paywall `.pw-sheet` | MUI `Dialog` / Superwall paywall |
| `.card` / `.tile` rows | MUI `Card` / `Paper` |
| `.cta`, `.send` | MUI `Button` (warm gradient) |
| `<textarea>` | MUI `TextField` (multiline) |
| inline `<svg>` / emoji | `@mui/icons-material` · `lucide-react` |

## Mockups
| Screen | Files |
|--------|-------|
| Onboarding *(flow)* | [`mockups/onboarding.html`](mockups/onboarding.html) · [`mockups/onboarding.png`](mockups/onboarding.png) |
| Home | [`mockups/home.html`](mockups/home.html) · [`mockups/home.png`](mockups/home.png) |
| Practice | [`mockups/practice.html`](mockups/practice.html) · [`mockups/practice.png`](mockups/practice.png) |
| Profile | [`mockups/profile.html`](mockups/profile.html) · [`mockups/profile.png`](mockups/profile.png) |
| Witty+ paywall | [`mockups/paywall.html`](mockups/paywall.html) · [`mockups/paywall.png`](mockups/paywall.png) |

Bottom tabs (left→right): **Home · Practice · Role play** *(soon)* **· Profile.** A
Telegram-community button sits just left of the persistent "Chat with us" bubble
(top-right, on every screen) — same placement as `../ux/`.

**Onboarding** is the same interactive *flow* in one file — tap an option / "Done" to walk
through all six steps (one trigger question → tiny practice → variable reward → login →
reminder → today's plan). Preview a stage with a hash, e.g. `onboarding.html#3` or
`onboarding.html#5perm`.

Open any `.html` in a browser (static preview). Regenerate the PNGs (one per screen):
```bash
for p in onboarding home practice profile paywall; do
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
    --force-device-scale-factor=2 --window-size=440,940 --virtual-time-budget=3500 \
    --screenshot="mockups/$p.png" "file://$PWD/mockups/$p.html"
done
```
