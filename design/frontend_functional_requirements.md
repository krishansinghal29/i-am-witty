# i-am-witty Frontend Functional Requirements

Source: `ux_existing/` mockups (`onboarding`, `home`, `practice`, `profile`, `paywall`), the UX visual brief (`ux_existing/README.md`), and the onboarding flow spec (`onboarding.md`). Aligned with `backend_functional_requirements.md`, `backend_lld.md`, and `database_schema.md`.

## Scope

These requirements describe the client/app capabilities needed to deliver the experience shown in the mockups. They are written to guide later screen, component, state, navigation, and integration design. Task-specific in-exercise interaction behavior is intentionally out of scope; tasks are treated as typed runtime units rendered by a shared UI per task type, to be detailed in later deep dives (mirroring the backend's treatment of tasks).

## Frontend-Relevant Tech Stack

The client stack, per the UX implementation brief:

- Ionic React (`@ionic/react`): UI component library and navigation shell, themed to "Light & Warm" by overriding Ionic CSS variables rather than restyling from scratch.
- Capacitor: native shell for iOS/Android and access to native APIs (push notifications, secure storage, in-app review where needed).
- React + TypeScript: application code, state, and view logic.
- RevenueCat SDK (client): fetch Offerings/packages, present the paywall, run purchase and restore flows, and read the `Witty+` entitlement.
- PostHog SDK (client): product analytics, feature flag evaluation, and session/replay capture where enabled.
- Supabase client: Apple/Google authentication and authenticated calls; most data access goes through backend APIs/Edge Functions.
- Capgo: over-the-air app update/release delivery.

Theming and content presentation are client concerns: the "Light & Warm" theme applied via Ionic CSS variables (light surfaces, orange accent for CTAs/celebration, blue for primary/active states), Inter as the app font, rounded line icons (~2px stroke), and a 12px radius token. The shipped app uses real photo personas for conversation practice; the mockups stand in with emoji thumbnails.

Note: the static HTML/CSS files in `ux_existing/mockups` are for design only. The phone frame, status bar, and dynamic island are mockup chrome and are not production UI.

## Main Frontend Requirements

### 1. App Shell, Navigation, and Theme

The frontend shall provide a themed app shell with persistent navigation.

Key frontend needs:
- Render a bottom tab bar with four tabs, left to right: Home, Practice, Role play (disabled, "Soon" badge), and Profile.
- Keep the active tab visually indicated (blue active state); render Role play as non-interactive until its feature flag is enabled.
- Render a persistent top-right action cluster on every primary screen: a Telegram-community button and a "Chat with us" bubble (with an unread/attention dot).
- Apply the "Light & Warm" theme via Ionic CSS variables (tokens and Inter font) globally.
- Route the user between the onboarding flow and the main tabbed app based on onboarding and authentication state.
- Respect device safe areas, status bar, and OS back behavior in the production shell.

### 2. Onboarding Flow

The frontend shall implement the six-step onboarding flow as a single interactive flow.

Key frontend needs:
- Run steps in order: (1) trigger question → (2) one tiny personalized practice → (3) variable reward → (4) login → (5) reminder → (6) land on Today's Plan.
- Show a top progress indicator across the onboarding steps; show the landing as complete.
- Provide back navigation between steps; hide Back on step 1; hide the onboarding top bar on the final landing.
- Step 1 — Trigger question: present a single-select question ("Where do you want to feel quicker?") with six options (Group chats, Dates, Work, With friends, On stage, When someone teases me); selecting one advances and personalizes later steps.
- Step 2 — Tiny practice: render the first task tuned to the chosen trigger (title, duration, type, tinted thumbnail, prompt/scenario); calm presentation with no confetti; offer a text input ("one line is plenty") and a "Say it out loud instead" voice option; show a privacy reassurance.
- Step 3 — Variable reward: present a loud celebration (confetti/glow) with a style label (e.g. "Quick Wit"), an echo of the user's take, a sharper rewrite, a tiny insight, and a first-step badge.
- Step 4 — Login after the win: prompt "Save your Day 1 streak?" with Continue with Apple, Continue with Google, and "Not now"; allow continuing without auth.
- Step 5 — Reminder: present reminder-time options (Before work, Before going out, After dinner, 8:00 PM) and "Not now"; trigger the OS notification permission prompt only after a time is picked.
- Step 6 — Landing: show a Today's-Plan preview with the just-completed first task marked done and a clear "Next up" item, then enter the app.
- Do not require login before the first practice; allow onboarding to resume if the user leaves before finishing.
- Persist onboarding state and the selected trigger to the backend, and record first-task completion and milestone prompts (first win, account prompt, reminder prompt).

### 3. Home — Today's Plan

The frontend shall render the user's daily plan as a guided path with one clear next step.

Key frontend needs:
- Show a header with a streak chip (🔥 + count), a weekly activity strip (Su–Sa) with per-day states (done ✓, missed ✕, today, upcoming), and the Telegram + chat actions.
- Show a greeting, the "Today's plan" title with a help affordance, and a low-pressure subtitle.
- Render the plan as an ordered vertical path with a rail of nodes (done, current, upcoming) and connectors between items.
- Emphasize exactly one "Next up" card (highlighted/glowing); render remaining items as upcoming.
- Render each item with a type-tinted thumbnail/emoji, title, duration, and type label.
- Open the task runtime when the user taps the next/an available item.
- Drive the screen from the daily-plan API and render without additional per-item lookups where practical; support resuming where the user left off.

### 4. Practice Library

The frontend shall provide a calm, low-pressure library of exercises to repeat any time.

Key frontend needs:
- Render a grid of exercise tiles, each with a type-tinted thumbnail, title, duration, and type label.
- Support the exercises shown in the mockups: Warm-up riff, Yes And, Box breathing, Peak–End hook, One-word story, Punch it up, 60-second story, and Power pose.
- Support optional filter chips by activity family (All, Improv, Sprints, Stories) and optional sections (e.g. "Your regulars"), as previewed in the paywall backdrop.
- Open the task runtime when a tile is tapped, subject to entitlement and the free daily limit.
- Keep the screen non-graded and pressure-free; distinct from Home's curated daily path.

### 5. Task Runtime (shared per task type)

The frontend shall render a shared task UI per task type, filled with per-task content and assets.

Key frontend needs:
- Render the shared UI structure indicated by the task type (`ui_schema_key`), populated by per-task content, image, thumbnail, and prompt data from the backend.
- Support the current task-type families: sprint (voice delivery), improv, calm/breath, and story/radio.
- Start a task attempt on entry and complete it on finish; reflect plan-item status changes.
- Keep recording and practice calm; trigger a loud celebration only on completion.
- Offer voice capture and/or text input per task type.
- Treat detailed per-type interaction, generation, and feedback rendering as out of scope here; the runtime should route to the appropriate task-type behavior defined in later deep dives.

### 6. Streaks, Progress, and Celebration

The frontend shall present progress gently and against the user's past self only.

Key frontend needs:
- Display streak count, the weekly activity strip, and the completed-exercises count.
- Express forgiving-streak behavior (never punish missed days) and reassure that the streak is safe when the free limit is reached.
- Trigger celebration effects (confetti, glow) only on wins (completing a task/round).
- Frame progress as XP/level vs. the past self; avoid leaderboards, public ranking, or harsh red scoring.

### 7. Subscription and Paywall (Witty+)

The frontend shall present the Witty+ paywall and enforce free-usage limits.

Key frontend needs:
- Present the paywall as a bottom sheet (Ionic `IonModal`, sheet style) shared by two triggers: reaching the daily free limit, and profile entry points (the "Go unlimited with Witty+" card and a Witty+ settings row).
- On the limit trigger, show a gentle, non-punishing banner ("that's your 3 free practices for today — your streak's safe").
- Render a feature list and two packages — Annual (`$rc_annual`, pre-selected, "Best value · save 44%") and Monthly (`$rc_monthly`) — plus a free-trial line, Restore link, and Terms/Privacy.
- Render live RevenueCat Offerings/packages and call `purchasePackage` / `restorePurchases`; always provide an easy "Maybe later" with no dark patterns.
- Enforce the free daily limit of three tasks for non-subscribers, coordinated with backend state, and surface the paywall when the limit is reached.
- Gate access on the `Witty+` entitlement and reflect entitlement-dependent UI (unlimited practice, full library, Role play when available, no ads).

### 8. Profile

The frontend shall present a private profile focused on personal progress.

Key frontend needs:
- Show a hero with avatar and display name.
- Show a stat duo: day streak and exercises completed.
- Show a Witty+ upsell card that opens the paywall sheet.
- Show a menu with "Join our Telegram community" and "Chat with us" entries.
- Provide a Sign out action.
- Keep the framing private and comparison-free (vs. past self), consistent with the brief.

### 9. Support and Community ("Chat with us")

The frontend shall provide an always-available support entry point and community link.

Key frontend needs:
- Expose a persistent "Chat with us" bubble on every primary screen that opens a bottom sheet.
- Provide a free-text message input, submit it to the backend support endpoint, and show a confirmation state after sending.
- Frame the channel as private and human-read; record the source screen with the submission.
- Provide a Telegram-community button that opens the external community link from app config.

### 10. Reminders and Notifications

The frontend shall let users set a daily warm-up reminder and manage notification permission.

Key frontend needs:
- Present reminder-time selection during onboarding (and allow it to be reviewed/updated later).
- Request OS notification permission via Capacitor only after the user picks a reminder time; never before.
- Persist the reminder preference and timing to the backend and register the device/push token and permission state.
- Support skipping or clearing the reminder, reflecting "skipped/enabled/disabled" states.

### 11. Identity and Authentication

The frontend shall support guest use first, then optional sign-in that preserves progress.

Key frontend needs:
- Establish a guest/anonymous session locally and via the backend before login, so onboarding and the first task work without authentication.
- Support Apple and Google sign-in through Supabase.
- Link guest progress to the authenticated account on sign-in.
- Support sign-out and session invalidation.
- Store and read the durable app identity/session needed for authenticated API calls.

### 12. Configuration, Feature Flags, and Updates

The frontend shall adapt to backend/remote configuration.

Key frontend needs:
- Read public app configuration (Telegram, Terms, Privacy links; free-task limit).
- Evaluate feature flags via PostHog and gate future/unavailable areas (Role play renders disabled with a "Soon" badge).
- Apply Capgo over-the-air updates and account for app version/release channel where behavior depends on it.
- Emit product analytics events for key actions where applicable.

### 13. Cross-Cutting UX Requirements

The frontend shall handle the states and accessibility concerns common to all screens.

Key frontend needs:
- Provide loading, empty, and error states for data-backed screens (plan, catalog, profile, paywall offerings).
- Honor reduced-motion preferences for confetti/glow and other celebration animations.
- Maintain readable contrast on the dark theme and consistent rounded iconography.
- Surface privacy reassurances where the user is asked to produce content.
- Keep optimistic/responsive interactions where it lowers perceived pressure (e.g. immediate "Next up" emphasis).

## Screen Inventory

| Screen | Key elements | Primary backend operations |
|--------|--------------|----------------------------|
| Onboarding (flow) | Trigger question, tiny practice, variable reward, login, reminder, plan landing | Create guest session, save trigger, assign first task, start/complete attempt, link auth user, save reminder |
| Home | Streak chip, week strip, Today's plan path, Next-up card | Get/create today's plan, compute progress summary, start attempt |
| Practice | Exercise grid, filters, sections | Get practice catalog, get task runtime, start attempt |
| Task runtime | Shared per-type UI, content/assets, attempt lifecycle | Get task runtime, start attempt, complete attempt, check limit/entitlement |
| Paywall (Witty+) | Limit banner, feature list, Annual/Monthly packages, trial, restore | Read RevenueCat offerings, purchase/restore, refresh entitlement |
| Profile | Hero, stat duo, Witty+ upsell, community/support menu, sign out | Read profile/progress, open paywall, submit support, sign out |
| Chat sheet | Message input, send, confirmation | Submit support message |

## Implied Frontend State and Data

- Onboarding state and selected trigger.
- Guest/auth session and durable app identity.
- Subscription entitlement and free-limit/usage state.
- Today's daily plan and ordered plan items.
- Practice task catalog with task-type UI metadata.
- Task runtime payloads and per-attempt state.
- Progress summary: streak, completed count, weekly activity.
- Reminder preference and notification permission/device state.
- Support sheet draft and submission status.
- RevenueCat offerings/packages and purchase status.
- App configuration, external links, and feature flags.

## Out Of Scope For This Pass

- Detailed in-exercise interaction, generation, and feedback UI for each task type.
- Exact component tree, styling specifics, and animation timings.
- Exact API route names and payloads.
- Role play screens and behavior (future, flag-gated).
- Detailed analytics event taxonomy.
- Offline/sync strategy beyond basic resume behavior.
