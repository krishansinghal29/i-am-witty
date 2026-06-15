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
HTML sources live in [`mockups/html/`](mockups/html/); rendered PNGs in [`mockups/images/`](mockups/images/).

| Screen | Files |
|--------|-------|
| Onboarding *(flow)* | [`mockups/html/onboarding.html`](mockups/html/onboarding.html) · [`mockups/images/onboarding.png`](mockups/images/onboarding.png) |
| Home | [`mockups/html/home.html`](mockups/html/home.html) · [`mockups/images/home.png`](mockups/images/home.png) |
| Practice | [`mockups/html/practice.html`](mockups/html/practice.html) · [`mockups/images/practice.png`](mockups/images/practice.png) |
| Profile | [`mockups/html/profile.html`](mockups/html/profile.html) · [`mockups/images/profile.png`](mockups/images/profile.png) |
| Witty+ paywall | [`mockups/html/paywall.html`](mockups/html/paywall.html) · [`mockups/images/paywall.png`](mockups/images/paywall.png) |
| **Loading states** *(Spark loader)* | [`mockups/html/loading.html`](mockups/html/loading.html) · [`mockups/images/loading.png`](mockups/images/loading.png) |
| **Role play** | [`mockups/html/roleplay.html`](mockups/html/roleplay.html) · [`mockups/images/roleplay.png`](mockups/images/roleplay.png) · [`roleplay-listen.png`](mockups/images/roleplay-listen.png) |

### Task runtime *(the three task types)*
A new, focused **in-exercise** design (a calm full-screen runtime — not a tab). Each
file is one interactive flow with three phases — **Brief · Respond · Reflect**
(*Rehearse* for the scaffolded type) — walkable by tapping the segmented bar under the
header (default frame = *Respond*). The shared shell (exit · title · `?` help · phase bar
· big record ring · gentle 4-part feedback + *Better Way*) is identical across all three;
only the **prompt shape** and **response guidance** change per type. These map 1:1 to the
runtime task types in [`../../tasks_trimmed.md`](../../tasks_trimmed.md).

**Timing model (why there's a Brief).** The user only controls timing on the **Brief** —
the up-front explainer of what the exercise is and how it works. Once they tap *Start*,
the prompt is **spoken automatically** (no optional "hear it") and the **mic opens on its
own** — there is **no "I'm ready" gate** after the prompt appears, so there's no window to
over-rehearse. The Brief sets that expectation ("react, don't rehearse"); the Respond
screen marks the prompt as auto-voiced (speaker + equalizer) and shows a live *Recording*
state. Chrome and the `🔒 private` label were dropped from this focused mode to cut
clutter.

| Task type | Representative | What's different | Files |
|-----------|----------------|------------------|-------|
| `voice_single_prompt` | *Misinterpretation: Techniques* | one `She` line **+ a runtime-assigned technique card** | [`mockups/html/task-single-prompt.html`](mockups/html/task-single-prompt.html) · [`mockups/images/task-single-prompt.png`](mockups/images/task-single-prompt.png) |
| `voice_dialogue_prompt` | *Question Answer Tease* | a generated **`You → She` exchange** (chat bubbles) sets the scene | [`mockups/html/task-dialogue-prompt.html`](mockups/html/task-dialogue-prompt.html) · [`mockups/images/task-dialogue-prompt.png`](mockups/images/task-dialogue-prompt.png) |
| `voice_scaffolded_prompt` | *Push / Pull* | one `She` scenario rehearsed through a **3-step stepper** (Push → Pull → Combine); only the final combine is scored | [`mockups/html/task-scaffolded-prompt.html`](mockups/html/task-scaffolded-prompt.html) · [`mockups/images/task-scaffolded-prompt.png`](mockups/images/task-scaffolded-prompt.png) |

Roles render as **speaker chips** (`She` = rosy/coral avatar, `You` = blue) per the
runtime's role table. Actions are **blue** (primary), with **orange** reserved for the
"submit / get feedback" warmth and celebration — a deliberately calmer, more playful take
than the current orange-heavy `../../frontend/` sprint UI.

Bottom tabs (left→right): **Home · Practice · Role play** *(soon)* **· Profile.** A
Telegram-community button sits just left of the persistent "Chat with us" bubble
(top-right, on every screen) — same placement as `../ux/`.

**Onboarding** is the same interactive *flow* in one file — tap an option / "Done" to walk
through all six steps (one trigger question → tiny practice → variable reward → login →
reminder → today's plan). Preview a stage with a hash, e.g. `html/onboarding.html#3` or
`html/onboarding.html#5perm`.

### Role play *(live spoken conversation)*
A full-screen **role-play runtime** — a live, voiced conversation with an AI persona
(*Maya*) over an **illustrated avatar background** (a warm, softly-lit rooftop-party scene,
all inline SVG so the file is self-contained). The top pins a close (✕), the persona name,
an options button, the **task progress** (`Land a push-pull · 1 / 5`, 5-segment bar) and a
**hint** — the *scenario itself* is set once, in the chat thread (a narration line), so it
isn't duplicated up top.

Below is a scrollable chat thread where every **AI (Maya) line carries a ▶ play button**;
roles follow the runtime role table — **Maya (She)** = rosy/coral accent on a frosted-white
bubble, **You** = blue cool-gradient bubble — over a warm bottom **scrim** so the thread
reads. The bottom **text bar** has **Send** + **Speak**: tapping **Speak** opens the mic
with a live *Listening…* state — the field morphs into a red dot + waveform and the mic
glows/ripples. Preview that state via hash: `roleplay.html#listen`.

### Loading states — "Spark loader"
Replaces the plain `IonSpinner` crescent with a calm, branded loader: the **riffy mark**
breathes inside a chasing **blue→orange ring**, three orbiting accent dots, and gentle
**voice equalizer bars** (same bob animation as the task runtime mockups). Four placements:

| Variant | Use in app | Message |
|---------|------------|---------|
| **Boot** | `AuthGuard` · `OnboardingGuard` session resolve | optional ("Starting up…") |
| **In-page** | `LoadingView` on Home, Practice, Profile, task host | contextual copy |
| **Sheet** | Paywall offerings, modal fetches | short label |
| **Compact** | `Button` `loading` prop, inline auth steps | beside label or icon-only |

Motion stays **slow & ease-in-out** (2–3s loops). `prefers-reduced-motion` falls back to
a static mark with an opacity pulse — no spinning. Preview all variants in
[`mockups/html/loading.html`](mockups/html/loading.html).

Open any file in [`mockups/html/`](mockups/html/) in a browser (static preview). Regenerate
the PNGs into [`mockups/images/`](mockups/images/) (one per screen):
```bash
for p in onboarding home practice profile paywall loading roleplay \
         task-single-prompt task-dialogue-prompt task-scaffolded-prompt; do
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
    --force-device-scale-factor=2 --window-size=560,940 --virtual-time-budget=3500 \
    --screenshot="mockups/images/$p.png" "file://$PWD/mockups/html/$p.html"
done
# Role play has an extra "mic open" state (note: the #fragment goes AFTER .html):
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --force-device-scale-factor=2 --window-size=560,940 --virtual-time-budget=3500 \
  --screenshot="mockups/images/roleplay-listen.png" "file://$PWD/mockups/html/roleplay.html#listen"
```
> **Window width must stay wider than the phone.** The mockups center a 392px `.phone`
> (plus a ~12px `box-shadow` bezel and a soft drop shadow) inside the page, so headless
> Chrome lays it out in a viewport ~485px wide. A capture window narrower than that (the
> old `440`) crops the bitmap before the right bezel, shearing the device frame on the
> right. `560` leaves balanced margins on both sides — don't drop it back below ~500.
