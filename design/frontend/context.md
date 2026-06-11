# i-am-witty Frontend — Context & Handoff

This document is the single source of truth for an agent continuing the **frontend** build
in `design/frontend`. It covers what exists, what's left, how to run everything, the **real**
backend API contract, and the conventions to follow.

> Status (handoff point): **Foundations complete and verified end-to-end.** Scaffold, theme,
> data layer, integration ports, real vendor adapters, composition root, app shell, routing,
> guards, and guest-session/config bootstrap are all in place, typecheck-clean, and the app
> boots in a browser against the live backend (a guest session is minted, config loads, and a
> new guest is correctly redirected to `/onboarding`). **No real screens yet** — only placeholder
> `IonPage` stubs. The next milestone is building the actual screens.

---

## 1. What this app is

AI-assisted practice app for humour / communication / confidence, for an "anxious introvert"
practicing in private. Light & Warm theme. **Three first-class delivery targets — iOS, Android, and
Web — all of which must run end-to-end and be functionally complete.** The product UX is **optimized
for the mobile app**; the **web UX may be partially refined** (functional parity is required, but web
polish/responsive layout is allowed to lag the app — never ship web-broken, just web-less-polished).
The frontend talks to a **FastAPI backend** (already built) in `design/backend`.

## 2. Tech stack (installed, pinned)

- **Ionic React 8.5** + **React 19** + **Vite 5** + **TypeScript** (strict). Ionic uses **React Router v5**.
- **@tanstack/react-query v5** (server state) + **zustand v5** (UI/transient state).
- **Capacitor 8** (native shell) with plugins: `app, status-bar, keyboard, haptics, preferences, push-notifications`, `@capacitor-community/speech-recognition`, `@aparajita/capacitor-secure-storage`.
- **Real vendor SDKs**: `firebase` + `@capacitor-firebase/authentication` (auth), `@revenuecat/purchases-capacitor` (subscriptions), `posthog-js` (analytics/flags), `@capgo/capacitor-updater` (OTA). Deepgram STT is reached via raw WebSocket using a backend-minted token (no SDK).
- Path alias **`@/* → src/*`** (`tsconfig.json` `paths` + `vite-tsconfig-paths`; note: no `baseUrl`, targets are `./src/*`).
- Native platforms `ios/` and `android/` are added (all 11 plugins wired). One SPM warning on speech-recognition for native iOS builds — resolve in Xcode later; irrelevant for web.

### Platform targets (iOS / Android / Web) — all first-class

All three ship and must work **end-to-end and functionally complete**. UX is optimized for the **mobile app**;
the **web UX may be partially refined** (functional parity required; web polish/responsive layout can lag). Build
screens mobile-first via Ionic components (which adapt to web), but verify every flow works in the browser too.

Per-integration platform support (today):

| Capability | iOS | Android | Web | Notes |
|---|---|---|---|---|
| Auth (Firebase) | ✓ native plugin | ✓ native plugin | ✓ popup/redirect | works on all three |
| Analytics/flags (PostHog) | ✓ | ✓ | ✓ | `posthog-js` works in webview + browser |
| STT (Deepgram WS + mic) | ✓ | ✓ | ✓ | `getUserMedia` + Web Audio PCM → Deepgram (`linear16`, nova-3); one path, no native fallback; text entry always available |
| Secure storage | ✓ keychain/keystore | ✓ | ✓ IndexedDB/localStorage fallback | web functional, less secure |
| Push notifications | ✓ | ✓ | ✗ today | web needs Web Push (not wired); reminder pref still persists server-side, OS push degrades |
| Subscriptions (RevenueCat) | ✓ purchases-capacitor | ✓ | ✗ today | `purchases-capacitor` has **no web purchase** path — see decision below |
| OTA (Capgo) | ✓ | ✓ | n/a | web deploys are static hosting; updater no-ops on web |

**For a complete web build, two product decisions are required** (the adapters already degrade gracefully so web still runs):
- **Web subscriptions**: choose a web purchase path (RevenueCat **Web Billing** / Stripe) or gate the web paywall to
  "subscribe in the app". `RevenueCatSubscriptionGateway` currently no-ops purchases on web.
- **Web push / reminders**: either wire Web Push, or accept that web saves the reminder preference (server-side) without
  an OS push and relies on the native apps for delivery.

## 3. How to run

**Backend** (from `design/backend`, uses `uv` + a Neon Postgres already migrated & seeded):
```bash
uv run uvicorn app.api.main:app --host 127.0.0.1 --port 8000
# health check: curl http://127.0.0.1:8000/health  -> {"status":"ok","db":"ok"}
```
**Frontend** (from `design/frontend`):
```bash
npm run dev -- --port 5173 --strictPort     # http://localhost:5173
npm run build        # tsc + vite build (CI gate)
npx tsc --noEmit     # typecheck only
npx cap sync ios|android   # after native-relevant changes
```
**Env**: `design/frontend/.env` (gitignored; `.env.example` committed). `VITE_API_BASE_URL=http://localhost:8000`.
`VITE_POSTHOG_KEY` is set. Firebase / RevenueCat keys are **empty** — those adapters no-op/throw gracefully
until filled (sign-in and purchases need real keys + native builds; everything else runs without them).

## 4. Backend context (design/backend)

- Python **FastAPI** (ports-and-adapters), **Neon Postgres** via SQLAlchemy async + asyncpg, Alembic migrations.
  `DATABASE_URL` = pooled (app), `DATABASE_URL_DIRECT` = non-pooled (Alembic). DB is **already migrated + seeded**.
- **Integrations are lazy** (no creds/network touched at startup). Real adapters exist for Firebase (token verify),
  RevenueCat (entitlement truth via webhook), PostHog, Deepgram (STT). The **task generation + evaluation engine is a
  deterministic FAKE** (`FakeTaskRuntimeEngine`) — so completing a task returns canned `feedback_html`/`sample_answer_html`.
  Good enough to build all screens; a real LLM engine is a later backend swap.
- **CORS** (required for the **web target** — production, not just dev): a CORS middleware was added in
  `design/backend/app/api/main.py` allowing `http://localhost:5173`, `http://127.0.0.1:5173`, `capacitor://localhost`,
  `http://localhost`. The deployed **web origin(s) must be added here for production**. Native Capacitor isn't subject to
  CORS. This is the only backend change made during the frontend build.
- **Seeded data**: 3 tasks (the representatives) — `misinterpretation-techniques` (`voice_single_prompt`),
  `question-answer-tease` (`voice_dialogue_prompt`), `push-pull` (`voice_scaffolded_prompt`); all `access_tier=free`,
  `thumbnail_key`/`image_key` = slug. `app_config`: `free_task_limit=3`, `telegram_community_url`, `terms_url`,
  `privacy_url`. Feature gates: `role_play` (req. `riffy_plus`), `riffy_plus`, `premium_task_library` (req. `riffy_plus`).

## 5. Authoritative API contract (use THIS, not the idealized DTOs in `frontend_lld.md`)

All app routes under `/v1`. **Auth header**: `Authorization: Bearer <firebaseIdToken>` when signed in, else
`X-Guest-Token: <session_token>`. `GET /v1/config` needs no auth.

| Method & path | Request | Response |
|---|---|---|
| `POST /v1/guest-sessions` | `{timezone, locale?}` | `{app_user_id, status, session_token, timezone}` |
| `POST /v1/auth/link` | `{id_token}` | `{app_user_id, status, firebase_uid, timezone}` |
| `GET /v1/onboarding` | — | `{current_step, selected_trigger, first_task_id, first_task_attempt_id, completed_at}` |
| `PATCH /v1/onboarding` | `{trigger}` | onboarding state (same shape) |
| `GET /v1/config` | — | `{values{}, free_task_limit, feature_gates[{feature_key, default_enabled, requires_entitlement, min_app_version}]}` |
| `GET /v1/home` | — | `{plan{id, plan_date, status, items[{id, task_id, position, status, current_attempt_id}]}, progress{completed_task_count, current_streak_count, longest_streak_count, last_activity_date}, access{is_riffy_plus}, onboarding{…}}` |
| `GET /v1/catalog` | — | `[{task{id, slug, title, description, task_type_id, duration_seconds, thumbnail_key, image_key, access_tier, status, sort_order}, requires_premium, is_locked}]` |
| `POST /v1/tasks/{id}/runtime` | `{source, daily_plan_item_id?}` | `{attempt_id, task, task_type{id, display_name, ui_schema_key, runtime_engine_key}, payload{prompt{messages[{role, content}], speech_text}, assigned_technique|null, scaffold_stages[], audio_base64, audio_content_type, avatar_image_url}}` |
| `POST /v1/tasks/{id}/start` | `{source, daily_plan_item_id?}` | `{attempt_id, task_id, status, free_limit{allowed, should_paywall, remaining, reason}}` |
| `POST /v1/attempts/{id}/complete` | `{client_transcript?, audio_base64?, content_type?, language?, stage_responses[{position, transcript}]}` | `{attempt_id, status, result{style_label, feedback_html, sample_answer_html, completion_metadata}, free_limit{…}, streak{current_streak, longest_streak, last_qualified_date}}` |
| `POST /v1/transcription-tokens` | — | `{token, expires_at, provider, extra}` |
| `GET/PUT/DELETE /v1/reminders` | PUT `{status, timing_key?, local_time?, timezone}` | `{status, timing_key, local_time, timezone}` (GET may be `null`) |
| `POST /v1/notification-devices` | `{device_key, platform, push_token?, permission_status, app_version?, release_channel?}` | device record |
| `POST /v1/support-messages` | `{message_text, source_screen?}` | `{id, status, created_at}` |
| `GET /v1/me/access` | — | `{is_riffy_plus, entitlements[{entitlement_key, status, product_id, current_period_ends_at, trial_ends_at}]}` |
| `POST /v1/webhooks/revenuecat` | (RevenueCat → backend; not called by client) | — |

**Enums confirmed from backend source:**
- `selected_trigger` / `PATCH /v1/onboarding` `trigger` ∈ `group_chats, dates, work, friends, stage, teased`
  (= UX options Group chats / Dates / Work / With friends / On stage / When someone teases me).
- `current_step` starts at `trigger_question`, advances to `first_task` after the trigger is saved.
  **The full `OnboardingStep` enum lives in `design/backend/app/infrastructure/db/orm/onboarding.py` — read it before
  building the onboarding flow** (the frontend `OnboardingStep` type is a `| string` union so it won't break, but the
  6-step UX needs the exact backend step names mapped).
- `ui_schema_key` ∈ `voice_single_prompt_v1, voice_dialogue_prompt_v1, voice_scaffolded_prompt_v1`
  (all share `runtime_engine_key = voice_prompt_v1`).

## 6. ⚠️ Known contract gaps / things to confirm before screens

1. **Runtime response is missing the `content` block.** `POST /v1/tasks/{id}/runtime` returns `task`, `task_type`,
   and generated `payload`, but NOT the `content` fields (`prompt_label`, `response_instruction`,
   `recording_limit_seconds`, `feedback_tabs`) that `tasks_trimmed.md` and the voice runtime shell need to render
   labels/limits/tabs. **Decision needed**: have the backend add `content` to that response (recommended — single source
   of truth), or derive defaults client-side. `TaskRuntime`/`RuntimePayload` types currently model only what's returned.
2. **Onboarding step names**: confirm the full backend `OnboardingStep` enum and map the 6 UX steps to it (see §5).
3. **Transcription**: `POST /v1/transcription-tokens` mints via the real Deepgram provider (key now in backend `.env`).
   Confirm the returned `{token, provider, extra}` is usable by the client WS path in
   `deepgram_transcription_gateway.ts` (subprotocol `['token', token]`). The text-entry fallback always works regardless.
4. **No separate endpoints** for free-limit, progress, or RevenueCat offerings: free-limit is **inline** in start/complete
   responses; progress+plan+access+onboarding are **bundled** in `GET /v1/home`; offerings come from the RevenueCat **SDK**.
5. **Web target completeness**: subscriptions and push are native-only today — see the Platform-targets table (§2) for the
   two web decisions (web billing path; web push vs. degraded reminders). Web must still run fully end-to-end otherwise.

## 7. Frontend architecture (layering — keep this honest)

```
Ionic Page (screen)  ->  Feature Hook (view-model)  ->  TanStack Query + Zustand stores
                                                    ->  Data layer (RiffyApi + http_client + mappers)
                                                    ->  Integration adapters (ports over vendor SDKs)
```
Rules: screens depend on feature hooks (never on the API client or an SDK). Hooks depend on the data layer + stores +
ports (never on `fetch`/Firebase/RevenueCat/PostHog/Capacitor directly). DTO shapes never leak into components (mappers
convert DTO→`@/types/models`). Vendors are reached only through `@/integrations/ports/*`, wired in the composition root.

## 8. What's DONE (files that exist and are typecheck-clean)

- **Scaffold/config**: `package.json`, `vite.config.ts` (+ tsconfig-paths), `tsconfig.json` (`@/*` alias),
  `capacitor.config.ts` (`appId: com.iamwitty.app`), `.env`/`.env.example`, `src/vite-env.d.ts` (typed `import.meta.env`),
  `index.html` (Inter font), `ios/` + `android/`.
- **Theme** (`src/theme/`): `tokens.ts` (Light & Warm palette/gradients/shadows/radius/font), `ionic_variables.css`
  (Ionic CSS var overrides + `--app-*` props + custom `accent` color), imported via `variables.css`.
- **Core types/libs**: `src/types/models.ts` (all camelCase view-models), `src/data/errors/app_error.ts` (`AppError`
  with `fromHttp`), `src/lib/result.ts`, `src/lib/reduced_motion.ts`.
- **Data layer** (`src/data/`): `dto/*` (snake_case wire shapes), `api/http_client.ts` (`createHttpClient` — attaches
  Bearer/X-Guest-Token via a `TokenProvider`, normalizes errors → `AppError`), `api/endpoints.ts`, `mappers/*`
  (DTO→model; `task_runtime_mapper` regroups `audio_base64`→`payload.audio`), `api/riffy_api.ts`
  (`createRiffyApi(http)` → 17 typed methods returning models).
- **Integration ports** (`src/integrations/ports/`): `AuthGateway, SubscriptionGateway, AnalyticsGateway,
  DeviceServices, SecureStore, TranscriptionGateway` (+ `index.ts` barrel).
- **Real vendor adapters**: `firebase/firebase_auth_gateway.ts` (+ `firebase_app.ts`), `revenuecat/…`, `posthog/…`,
  `capacitor/capacitor_secure_store.ts` + `capacitor_device_services.ts`, `transcription/deepgram_transcription_gateway.ts`,
  `capgo/capgo_updater.ts`. All degrade gracefully on web / without keys.
- **State** (`src/state/`): `query_keys.ts` (`session, config, onboarding, home, catalog, taskRuntime(id), access,
  reminder, offerings`), `query_client.ts` (no-retry on 4xx), `stores/{ui_store, onboarding_store, runtime_store}.ts`.
- **Composition root** (`src/app/providers.tsx`): builds adapters, `TokenProvider` → `http` → `RiffyApi`, `queryClient`,
  owns `setupIonicReact` + theme CSS, exposes `IntegrationsContext` + hooks `useIntegrations/useRiffyApi/useAuth/…`.
  Exports `STORAGE_KEYS` (`riffy.guest_session_token`, `riffy.app_user_id`).
- **Bootstrap hooks**: `features/identity/use_session.ts` (guest-first session bootstrap), `features/config/use_app_config.ts`,
  `features/onboarding/use_onboarding_state.ts`.
- **Guards** (`src/app/guards/`): `AuthGuard` (bootstrap gate, fail-open), `OnboardingGuard` (redirect to `/onboarding`
  until complete, fail-open), `useEntitlementGate` (action guard → opens paywall via `ui_store`).
- **Shell/routing** (`src/app/routes.tsx`, `src/app/App.tsx`, `src/main.tsx`): IonTabs (Home / Practice /
  Role-play "Soon" disabled / Profile) + full-screen `/onboarding` and `/task/:taskId`.
- **Placeholder screens** (`src/screens/**`): `HomePage, PracticePage, ProfilePage, OnboardingFlowPage,
  TaskRuntimePage` (IonPage stubs) and `PaywallSheet, SupportSheet` (sheet content stubs). **These are the things to replace.**

## 9. What's LEFT (the next milestone — real screens + feature hooks)

Build the real screens (replace the stubs) and their feature hooks. Suggested order — do **one vertical slice first**
(Onboarding → first voice task runtime → Home) to exercise the whole stack, then fan out. Planned files per `frontend_lld.md`:

- **Onboarding flow** (`screens/onboarding/onboarding_flow_page.tsx` + `steps/*`): 6 steps — trigger question →
  tiny practice (first task, calm) → variable reward (celebration) → login (Apple/Google/Not now) → reminder → plan landing.
  Hooks: extend `features/onboarding/` (`use_onboarding.ts`, `onboarding_machine.ts`), `features/identity/use_link_account.ts`,
  `features/reminders/use_reminder.ts`. The critical "first win" path.
- **Home** (`screens/home/home_page.tsx`): streak chip, week strip (Su–Sa), Today's-Plan path with one highlighted
  "Next up". Hook `features/home/use_today_plan.ts` + `features/progress/use_progress_summary.ts` (both read `GET /v1/home`).
- **Practice** (`screens/practice/`): catalog grid + filters. Hook `features/practice/use_practice_catalog.ts` (`GET /v1/catalog`).
- **Task runtime** (`components/task_runtime/`): the main extensibility seam — a **host** + a **registry** keyed by
  `ui_schema_key` → full runtime views; the three voice views share a **`voice_prompt` family shell** (Brief → Respond →
  Reflect, record ring, live transcript via `TranscriptionGateway` + text fallback, scaffold stepper, 4-part feedback +
  "Better Way"). Hooks `features/task_runtime/use_task_runtime.ts` + `use_task_attempt.ts`. See `frontend_lld.md` §Task Runtime.
- **Paywall** (`screens/paywall/paywall_sheet.tsx`): IonModal sheet, live RevenueCat offerings, Annual/Monthly, restore.
  Hooks `features/entitlement/{use_entitlement, use_free_limit, use_paywall}.ts`.
- **Profile** (`screens/profile/`): hero, stat duo, Riffy+ upsell, community/support menu, sign out.
- **Support sheet** (`screens/support/support_sheet.tsx`): message input → `POST /v1/support-messages`. Hook `features/support/use_support.ts`.
- **Design-system primitives** (`components/ui/`): `Button, Card, Sheet, TintedThumbnail, StreakChip, WeekStrip, PlanPath,
  RecordRing, Celebration` (reduced-motion aware), `StateViews` (Loading/Empty/Error).
- **Cross-cutting**: per-screen Loading/Empty/Error via StateViews; analytics events emitted from hooks (one seam);
  feature-flag gate Role play via `AnalyticsGateway.isFeatureEnabled('role_play')`; persistent top-right Telegram + "Chat
  with us" cluster rendered by the tab shell.

## 10. State management & cache invalidation (the client side of backend transactions)

Server state in TanStack Query keyed by `@/state/query_keys`. Because the backend bundles data, the invalidation set is:
```
completeTask success -> invalidate queryKeys.home (plan + progress) AND queryKeys.access (if a limit/paywall path changed it)
                        (free-limit comes back inline in the response; no separate key)
saveTrigger          -> invalidate queryKeys.onboarding, queryKeys.home (first task assigned)
linkAccount          -> invalidate queryKeys.session, queryKeys.home, queryKeys.access (guest progress merges)
purchase/restore     -> invalidate queryKeys.access (+ queryKeys.offerings)
saveReminder         -> queryKeys.reminder (and onboarding if in flow)
```
UI/transient state in Zustand: `ui_store` (sheets/paywall/support/attention dot), `onboarding_store` (selected trigger,
step index), `runtime_store` (attempt id, phase brief/respond/reflect, scaffold stage, recording, transcript).

## 11. Conventions

- TS strict, 2-space indent, single quotes, semicolons. Imports via `@/…` alias.
- React 19: no global `JSX` namespace — use `import type { ReactNode } from 'react'` for children props.
- Feature hooks consume `useRiffyApi()` / `useIntegrations()` from `@/app/providers` + `useQuery`/`useMutation`.
- Keep DTOs out of components; map in `data/mappers`. Add a new task type by adding a `ui_schema_key` + a runtime view +
  one registry line (see `frontend_lld.md` §"Adding a new task type").

## 12. Design references (in `design/`)

- `frontend_lld.md`, `frontend_functional_requirements.md` — frontend architecture + requirements.
- `tasks_trimmed.md` — task runtime contracts (payload/completion/evaluation, the 3 voice types, roles).
- `backend_lld.md`, `backend_functional_requirements.md`, `database_schema.md` — backend.
- `ux_existing/README.md` + `ux_existing/mockups/html/*.html` — **visual reference only** (legacy MUI/Tailwind mockups);
  we build in Ionic React. Screens: onboarding, home, practice, profile, paywall, task-single/dialogue/scaffolded-prompt.

## 13. Verified at handoff

`npm run build` + `npx tsc --noEmit` clean. Live run: backend `/health` `db:ok`; `GET /v1/config` returns seeded config;
`POST /v1/guest-sessions` mints a guest; `GET /v1/onboarding` returns `trigger_question`/not-complete; the app in-browser
boots, bootstraps a guest session, and `OnboardingGuard` redirects the new guest to `/onboarding` (placeholder renders).
Both dev servers (backend :8000, vite :5173) are how to reproduce.
