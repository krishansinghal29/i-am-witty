# i-am-witty Frontend LLD

Source: `frontend_functional_requirements.md`, `ux_existing/README.md` (and `ux_existing/mockups`), `tasks_trimmed.md`, and aligned with `backend_functional_requirements.md`, `backend_lld.md`, and `database_schema.md`.

## Goal

Define an Ionic React + TypeScript client structure that keeps screens and UI logic independent of vendor SDK details (Supabase, RevenueCat, PostHog, Capacitor, Capgo) and of backend payload shapes, while still fitting the current stack. SDK and transport code lives behind adapters/ports in one area so a vendor can be swapped with limited changes. Tasks of the same type render through one shared, data-driven runtime so new exercises are content, not new screens.

This document mirrors the layering discipline of `backend_lld.md`: the frontend's load-bearing decisions are **navigation/routing** and **state management** (the client analog of the backend's repositories and transactions).

## Frontend-Relevant Tech Stack

Per `frontend_functional_requirements.md` §0:

- Ionic React (`@ionic/react`): UI components and navigation shell, themed "Light & Warm" via Ionic CSS variables.
- Capacitor: native shell and native APIs (push notifications, secure storage, in-app review).
- React + TypeScript: application code, state, and view logic.
- RevenueCat SDK (client): Offerings/packages, paywall, purchase/restore, `Witty+` entitlement.
- PostHog SDK (client): analytics, feature flags, session replay where enabled.
- Supabase client: Apple/Google auth and authenticated calls; most data goes through backend APIs/Edge Functions.
- Capgo: over-the-air update/release delivery.
- Speech-to-text (STT): Deepgram (streaming) is the current recognizer for the voice task runtime, reached only through a `TranscriptionGateway` port so the provider is swappable (e.g. to a Whisper-based recognizer) without touching screens or the runtime contract. The provider key never ships in the client bundle: the backend mints short-lived credentials for the live path and owns the authoritative final transcript (see "Client vs. backend split for speech-to-text"). A native fallback (`@capacitor-community/speech-recognition` / Web Speech) can implement the same port for offline/cheap capture.

Note: the target client uses Ionic React per the functional requirements; the legacy shipped baseline in `ux_existing/README.md` (MUI v6 / Tailwind / framer-motion / Superwall) is documented there for visual comparison only and is not the architecture this LLD targets. The static `ux_existing/mockups/*.html` are design references, not production UI.

## Architectural Style

Use a feature-oriented layered structure with vendor isolation at the edges:

```text
Ionic Page (screen)
  -> View Hooks (feature view-models)
    -> Application State (server cache + UI stores)
    -> Data Layer (API client + DTO mappers)
    -> Integration Adapters (ports over vendor SDKs)
  -> Vendor SDKs / native plugins
```

Rules that keep this honest:

- Screens depend on feature hooks, never on the API client or an SDK directly.
- Feature hooks depend on the data layer and stores, never on `fetch`, Supabase, RevenueCat, PostHog, or Capacitor directly.
- The data layer maps backend DTOs to view models; DTO shapes never leak into components.
- Vendor SDKs are reached only through adapter interfaces (the client analog of backend repository/integration ports).

## Suggested Directory Structure

```text
frontend/
  src/
    app/
      App.tsx
      providers.tsx              # composition root: query client, theme, adapter wiring
      routes.tsx                 # route map and tab shell
      guards/
        onboarding_guard.tsx
        auth_guard.tsx
        entitlement_guard.tsx

    screens/
      onboarding/
        onboarding_flow_page.tsx
        steps/
          trigger_question_step.tsx
          tiny_practice_step.tsx
          variable_reward_step.tsx
          login_step.tsx
          reminder_step.tsx
          plan_landing_step.tsx
      home/
        home_page.tsx
      practice/
        practice_page.tsx
      task_runtime/
        task_runtime_page.tsx
      profile/
        profile_page.tsx
      paywall/
        paywall_sheet.tsx
      support/
        support_sheet.tsx

    features/
      identity/
        use_session.ts
        use_link_account.ts
      onboarding/
        use_onboarding.ts
        onboarding_machine.ts
      home/
        use_today_plan.ts
      practice/
        use_practice_catalog.ts
      task_runtime/
        use_task_runtime.ts        # fetch/resume runtime payload (generic, used by host)
        use_task_attempt.ts        # AttemptController: complete(body) + status (generic)
      progress/
        use_progress_summary.ts
      entitlement/
        use_entitlement.ts
        use_free_limit.ts
        use_paywall.ts
      reminders/
        use_reminder.ts
      support/
        use_support.ts
      config/
        use_app_config.ts
        use_feature_flag.ts

    components/
      ui/                        # design-system primitives bound to theme tokens
        button.tsx
        card.tsx
        sheet.tsx
        tinted_thumbnail.tsx
        streak_chip.tsx
        week_strip.tsx
        plan_path.tsx
        record_ring.tsx
        celebration.tsx
        state_views.tsx          # Loading / Empty / Error
      task_runtime/              # ui_schema_key -> full runtime views (registry-dispatched)
        host.tsx                 # thin dispatcher rendered by the page
        registry.ts              # ui_schema_key -> TaskRuntimeView
        contract.ts              # TaskRuntimeView props + attempt lifecycle contract
        families/                # shells shared by views of the same interaction shape (opt-in)
          voice_prompt/
            voice_prompt_shell.tsx
            phase_machine.ts       # Brief -> Respond (Rehearse) -> Reflect (voice-only)
            phase_bar.tsx
            feedback_panel.tsx
        views/                   # one full runtime view per ui_schema_key
          voice_single_prompt_v1.tsx     # composes the voice_prompt family
          voice_dialogue_prompt_v1.tsx   # composes the voice_prompt family
          voice_scaffolded_prompt_v1.tsx # composes the voice_prompt family
          # breathing_timer_v1.tsx       # future: its own shell, no record ring / transcript

    state/
      stores/
        ui_store.ts              # sheets, modals, transient UI
        onboarding_store.ts
        runtime_store.ts         # active attempt / phase / recording
      query_keys.ts

    data/
      api/
        http_client.ts
        endpoints.ts
      dto/
        plan_dto.ts
        task_runtime_dto.ts
        profile_dto.ts
        entitlement_dto.ts
      mappers/
        plan_mapper.ts
        task_runtime_mapper.ts
      errors/
        app_error.ts

    integrations/
      ports/
        auth_gateway.ts
        subscription_gateway.ts
        analytics_gateway.ts
        device_services.ts
        secure_store.ts
        transcription_gateway.ts
      supabase/
        supabase_auth_gateway.ts
      revenuecat/
        revenuecat_subscription_gateway.ts
      posthog/
        posthog_analytics_gateway.ts
      capacitor/
        capacitor_device_services.ts
        capacitor_secure_store.ts
      transcription/
        deepgram_transcription_gateway.ts   # streaming; live interim via backend-minted ephemeral key
        native_transcription_gateway.ts     # optional: Capacitor speech-recognition / Web Speech fallback
      capgo/
        capgo_updater.ts

    theme/
      tokens.ts                  # Light & Warm tokens
      ionic_variables.css

    types/
      models.ts                  # view-model types used across features

    lib/
      result.ts
      reduced_motion.ts
```

## Layer Responsibilities

### Screens (Ionic Pages)

Render `IonPage`/`IonContent` layout, wire user intent to feature hooks, and present loading/empty/error states. Screens hold no data fetching, no SDK calls, and no business rules. A screen reads a view model from a hook and renders it.

### Feature Hooks (View-Models)

The use-case layer of the client. Each hook composes server-state queries, UI stores, mappers, and adapters into a view model plus handlers for the screen. Examples:

- `useTodayPlan()` → ordered plan items, the single "next up", and `openTask(itemId)`.
- `useTaskRuntime(taskId)` → runtime payload, phase machine, `submit(transcript)`.
- `useEntitlement()` → `isWittyPlus`, and `useFreeLimit()` → remaining free tasks + `shouldPaywall`.
- `useOnboarding()` → current step, `selectTrigger`, `advance`, `back`.

Hooks decide *what the screen needs*; they do not know how the backend or an SDK provides it.

### Application State

Two clearly separated kinds of state, never conflated:

- **Server state** — anything owned by the backend (plan, catalog, progress, entitlement, config). Held in a query cache (recommended: TanStack Query) keyed by `query_keys.ts`, with explicit invalidation. Never copied into a global store.
- **Client/UI state** — transient and device-local (active onboarding step, open sheet, recording phase). Held in small stores (recommended: Zustand) or React context.
- **Durable identity state** — guest session token and app identity. Persisted through the `SecureStore` port (Capacitor Preferences / secure storage), read at startup.

### Data Layer

Owns transport and shape translation. The HTTP client attaches the Supabase access token when authenticated or the guest session token header otherwise, parses responses, and normalizes failures into one `AppError`. DTO types match backend payloads exactly (e.g. the runtime payload in `tasks_trimmed.md`); mappers convert DTOs into view-model types in `types/models.ts`. Components and screens never import DTO types.

### Integration Adapters (Ports)

TypeScript interfaces in `integrations/ports` describe what the app needs; vendor folders implement them. Screens and hooks depend on the port, not the SDK. If a vendor changes, replace the implementation under `integrations/<vendor>` while leaving features largely unchanged — the direct client analog of the backend's `infrastructure/repositories/*`.

## Navigation And Routing

Ionic React Router with an `IonTabs` shell for the main app and full-screen routes outside the tabs for focused flows.

```text
/onboarding            -> OnboardingFlowPage   (no tab shell; guarded: only until complete)
/app
  /home                -> HomePage             (tab 1)
  /practice            -> PracticePage         (tab 2)
  /roleplay            -> disabled "Soon"      (tab 3; feature-flag gated, non-interactive)
  /profile             -> ProfilePage          (tab 4)
/task/:taskId          -> TaskRuntimePage      (full-screen, outside tabs)
```

Modals/sheets are not routes: the paywall (`IonModal`, sheet style) and the "Chat with us" support sheet are opened via the `ui_store` from any primary screen.

Route guards (the highest-risk client logic — give them an explicit state machine):

- `OnboardingGuard`: if `onboarding_state.completed_at` is null, force `/onboarding` and resume at `current_step`; otherwise allow `/app`.
- `AuthGuard`: guest-first — never blocks the first practice. It exposes session state for screens that adapt (e.g. Profile sign-out), but does not gate routes pre-login.
- `EntitlementGuard` (action guard, not a route): before starting a task, `useFreeLimit()` decides whether to start the attempt or open the paywall sheet.

The persistent top-right cluster (Telegram button + "Chat with us" bubble with attention dot) and the bottom tab bar are rendered by the tab shell, not per screen.

## State Management Design

### Server state (query cache)

Centralize keys so invalidation is mechanical:

```ts
export const queryKeys = {
  session: ["session"] as const,
  config: ["config"] as const,
  onboarding: ["onboarding"] as const,
  todayPlan: ["plan", "today"] as const,
  practiceCatalog: ["practice", "catalog"] as const,
  taskRuntime: (taskId: string) => ["task", "runtime", taskId] as const,
  progress: ["progress", "summary"] as const,
  entitlement: ["entitlement"] as const,
  freeLimit: ["usage", "free-limit"] as const,
};
```

### Invalidation rules (the client side of backend transactions)

Completing a task is the multi-effect mutation; on success it must invalidate the same surfaces the backend wrote:

```text
completeTask success ->
  invalidate todayPlan          (plan item status, next-up)
  invalidate progress           (streak, completed count, week strip)
  invalidate freeLimit          (free tasks used today)
  invalidate entitlement        (only if a limit/paywall path changed it)
```

Other mutations and their invalidations:

```text
saveTrigger        -> onboarding, todayPlan (first task assignment)
linkAccount        -> session, progress, entitlement, freeLimit  (guest progress merges)
purchase/restore   -> entitlement, freeLimit
saveReminder       -> (no server-state read depends on it; update onboarding if in flow)
```

### Client/UI state

Small stores, each with a single concern:

- `ui_store`: which sheet/modal is open, attention-dot state.
- `onboarding_store`: derived step UI, selected trigger before persistence, progress indicator.
- `runtime_store`: active attempt id, current phase, recording status, captured transcript.

### Durable state

Read once at startup through `SecureStore`: guest session token, app user id, last-known onboarding completion. Written on guest-session creation and on auth link.

## Data Layer And API Client

```ts
// data/api/http_client.ts
export interface HttpClient {
  get<T>(path: string): Promise<T>;
  post<T>(path: string, body: unknown): Promise<T>;
}

// Implementation responsibilities:
// - attach Supabase access token if authenticated, else X-Guest-Session header
// - JSON encode/decode
// - map non-2xx and network failures to AppError (code + userMessage + cause)
```

DTOs mirror backend contracts verbatim. The task runtime DTO follows `tasks_trimmed.md`:

```ts
// data/dto/task_runtime_dto.ts
export interface TaskRuntimeDto {
  attempt_id: string;
  task: {
    id: string;
    slug: string;
    title: string;
    task_type_id: string;
    ui_schema_key: string;
    duration_seconds: number;
    thumbnail_key: string;
    image_key: string | null;
  };
  content: {
    prompt_label: string;
    response_instruction: string;
    recording_limit_seconds: number;
    feedback_tabs: { feedback_label: string; sample_answer_label: string };
  };
  prompt: { messages: { role: string; content: string }[]; speech_text: string | null };
  assigned_technique: { name: string; instruction: string; example: string } | null;
  scaffold_stages: ScaffoldStageDto[];
  audio: { audio_base64: string | null; content_type: string | null };
  avatar: { image_url: string | null };
}
```

Mappers convert DTOs to view models so the runtime renderer never sees backend field names directly.

Note the two `audio_base64` fields point in opposite directions and must not be conflated by the mapper: `TaskRuntimeDto.audio.audio_base64` is the **backend's TTS of the prompt**, played *to* the user in `Respond`; the `audio_base64` in the **completion body** is the **user's recorded answer**, sent *to* the backend (optional, for transcript confirmation/analysis — see `TranscriptionGateway`).

## Integration Adapters (Ports)

```ts
// integrations/ports/subscription_gateway.ts
export interface SubscriptionGateway {
  getOfferings(): Promise<Offering[]>;
  purchasePackage(pkg: PackageRef): Promise<EntitlementSnapshot>;
  restorePurchases(): Promise<EntitlementSnapshot>;
  getEntitlement(): Promise<EntitlementSnapshot>;
}

// integrations/ports/auth_gateway.ts
export interface AuthGateway {
  getSession(): Promise<Session | null>;
  signInWithApple(): Promise<Session>;
  signInWithGoogle(): Promise<Session>;
  signOut(): Promise<void>;
}

// integrations/ports/analytics_gateway.ts
export interface AnalyticsGateway {
  capture(event: string, props?: Record<string, unknown>): void;
  identify(appUserId: string, traits?: Record<string, unknown>): void;
  isFeatureEnabled(flag: string): boolean;
}

// integrations/ports/device_services.ts
export interface DeviceServices {
  requestNotificationPermission(): Promise<NotificationPermission>;
  getPushToken(): Promise<string | null>;
}

// integrations/ports/secure_store.ts
export interface SecureStore {
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
  remove(key: string): Promise<void>;
}

// integrations/ports/transcription_gateway.ts
// Shaped around what the app needs (mic in -> transcript + audio out), NOT around
// any one vendor's API, so a streaming provider (Deepgram) and a batch provider
// (Whisper) both fit. Live interim transcript is an OPTIONAL capability: a batch
// provider simply never emits it. Evaluation must never depend on a field only one
// provider can supply (e.g. pauseCount) — keep prosody metadata optional.
export interface TranscriptionResult {
  transcript: string;
  audioBase64: string | null;        // the USER's answer audio (optional upload for backend confirmation)
  contentType: string | null;
  durationSeconds: number;
  metadata?: TranscriptionMetadata;  // optional, provider-dependent
}
export interface TranscriptionMetadata {
  wordCount?: number;
  pauseCount?: number;               // needs word-level timings; not all providers expose this
}
export interface TranscriptionSession {
  onInterim?(cb: (partialTranscript: string) => void): void; // streaming providers emit; batch ones don't
  stop(): Promise<TranscriptionResult>;
  cancel(): Promise<void>;
}
export interface TranscriptionGateway {
  // Credentials for the live path are minted by the backend (never a static client key).
  startSession(opts: { recordingLimitSeconds: number; language?: string }): Promise<TranscriptionSession>;
  capabilities(): { streamingInterim: boolean };
}
```

`role_play` and `witty_plus` gates are read through `AnalyticsGateway.isFeatureEnabled` (PostHog), consistent with `feature_gate_defaults` on the backend.

### Client vs. backend split for auth and subscriptions

The Supabase and RevenueCat client SDKs are **triggers + optimistic reads**, not a source of truth. The auth and in-app-purchase *handshakes* must run on-device (native sign-in sheets; StoreKit/Play Billing payment sheets cannot be initiated from a server), so they stay in the client adapters. The backend remains the **authority**: it validates the JWT on every call, owns entitlement truth via the RevenueCat webhook (`revenue_cat_webhook` → `EntitlementService.sync_revenue_cat_event`), and enforces the daily free limit (`daily_limit_policy`). After purchase/restore, the client invalidates `entitlement` + `freeLimit` and re-reads the backend value. Rule: gate UX off the SDK read for snappiness, but never unlock a server resource on the client entitlement — the enforcement number is always the backend's `freeLimit`/`entitlement`.

### Client vs. backend split for speech-to-text (STT)

STT has **two latencies that behave oppositely**, so it is split into two paths rather than forced onto one:

- **Live interim transcript** (words on screen *while* speaking, during `Respond`) needs low latency. Routing this through our own backend adds a hop and a stateful proxy, so the client streams **directly to the provider** — but using a **short-lived credential minted by the backend** (`create_transcription_token` → `TranscriptionProvider.create_ephemeral_credential`), never a static key in the bundle. This live transcript is **best-effort and cosmetic**: the always-available text-entry fallback ("one line is plenty") covers any provider/network gap, and a batch provider that cannot stream simply omits it (`capabilities().streamingInterim === false`).
- **Final transcript** (the input to evaluation) is **backend-authoritative**. On completion the client posts its transcript plus the optional answer `audio_base64`; the backend produces or confirms the transcript before evaluating it. Latency here is effectively free: the `Reflect` step already waits on a multi-second LLM evaluation (the "analyzing" state), and backend STT pipelines inside that same window — the user is on the same loader either way.

Why this shape, and why it keeps the provider swappable:

- **The swap point is the backend.** Because the authoritative transcript is produced server-side, replacing Deepgram with a Whisper-style batch recognizer is largely a backend change; the client `TranscriptionGateway` contract (final transcript + audio + optional metadata) does not move.
- **Provider-specific tricks stay inside the adapter.** The ephemeral-key + streaming logic is Deepgram-shaped, but it lives entirely in `DeepgramTranscriptionGateway`. Swapping to a non-streaming provider replaces that adapter wholesale; we lose only the live-words nicety, not correctness.
- **No Deepgram-only dependency leaks into core logic.** `pauseCount` / word-level timings are optional `metadata`; the runtime, mapper, and (per `backend_lld.md`) evaluation degrade gracefully when a provider doesn't supply them.

Rule: the live transcript may come straight from the provider for snappiness, but the transcript that gets **evaluated and stored** is always the backend's — the client one is a draft.

## Component Architecture

Two tiers:

- **Design-system primitives** (`components/ui`): theme-bound building blocks — `Button` (warm gradient CTA), `Card`/`Tile`, `Sheet` (`IonModal`), `TintedThumbnail`, `StreakChip`, `WeekStrip` (Su–Sa states), `PlanPath` (rail of done/current/upcoming nodes + connectors), `RecordRing`, `Celebration` (confetti/glow, reduced-motion aware), and `StateViews` (Loading/Empty/Error). These read tokens from `theme/tokens.ts`; theming is changed only via Ionic CSS variables, never by restyling primitives per screen.
- **Feature components / screens** compose primitives with feature hooks.

Screen-to-data mapping (from the functional requirements' Screen Inventory):

| Screen | Hook(s) | Server reads |
|--------|---------|--------------|
| Onboarding | `useOnboarding`, `useTaskRuntime`, `useReminder`, `useLinkAccount` | onboarding, first-task runtime, reminder save |
| Home | `useTodayPlan`, `useProgressSummary` | today plan, progress summary |
| Practice | `usePracticeCatalog`, `useFreeLimit` | catalog, free-limit |
| Task runtime | `useTaskRuntime`, `useTaskAttempt` | runtime payload, start/complete attempt |
| Paywall | `usePaywall`, `useEntitlement` | offerings, entitlement |
| Profile | `useProgressSummary`, `useSession`, `usePaywall` | profile/progress |
| Support sheet | `useSupport` | submit support |

## Task Runtime (`ui_schema_key`-dispatched runtime views)

The frontend half of the backend's task-type/runtime split, and the client's main extensibility seam. The page is a thin **host**; a registry maps `ui_schema_key` → a **full runtime view that owns its own shell**. Views that share an interaction shape opt into a **family shell** for reuse; a view with a fundamentally different shape brings its own shell. This is the design rule the task-type model exists for: separate types only when the UI differs, and let "completely different UI" be additive rather than a special case.

### Host and registry

The page renders a dispatcher that owns nothing visual:

```tsx
// components/task_runtime/host.tsx (rendered by screens/task_runtime/task_runtime_page.tsx)
function TaskRuntimeHost() {
  const { taskId } = useParams();
  const { payload, attempt } = useTaskRuntime(taskId);
  const RuntimeView = taskRuntimeRegistry[payload.task.ui_schema_key] ?? UnsupportedRuntime;
  return <RuntimeView payload={payload} attempt={attempt} />;
}
```

The registry maps to **full views**, not inner panels:

```ts
// components/task_runtime/registry.ts
export const taskRuntimeRegistry: Record<string, TaskRuntimeView> = {
  voice_single_prompt_v1:     VoiceSinglePromptV1,     // ┐ all three compose the voice_prompt
  voice_dialogue_prompt_v1:   VoiceDialoguePromptV1,   // ┤ family shell (genuinely shared UI)
  voice_scaffolded_prompt_v1: VoiceScaffoldedPromptV1, // ┘
  // breathing_timer_v1:      BreathingTimerV1,        // future: its own shell, no record ring / transcript
};
```

### The voice family shell (opt-in reuse, not the universal page)

`families/voice_prompt/voice_prompt_shell.tsx` is reused by the three voice views because they share UI; it is not the page. It owns: exit, title, `?` help, the phase bar, the big record ring (with an always-available text-entry fallback), and the gentle 4-part feedback + "Better Way" panel — identical across the three voice views per `ux_existing/README.md`. A view for a different interaction shape ignores this shell entirely.

Phase machine (owned by the voice family; other families define their own phases), per the README's timing model:

```text
Brief  -> (user taps Start; user controls timing only here)
Respond -> prompt auto-voiced (TTS) and mic opens automatically by default; a text-entry
            fallback ("one line is plenty") is always available, and the calm onboarding
            first task uses a quiet variant (no auto-TTS, mic not auto-opened)
            (Scaffolded view inserts Rehearse stages: Push -> Pull -> Combine)
Reflect -> show feedback_html (What Landed / The Trap / Level Up / Mindset Shift)
            and sample_answer_html ("Better Way")
```

The `Respond` phase captures speech through the `TranscriptionGateway` port (never a vendor SDK directly): the live transcript shown over the record ring is the gateway's best-effort interim stream, while the value passed to `attempt.complete(body)` is the **final** transcript (plus optional answer `audio_base64`), which the backend re-confirms before evaluating. See "Client vs. backend split for speech-to-text".

Within the voice family, roles render as speaker chips (`She` = rosy/coral, `You` = blue) from the runtime role table. Actions are blue; orange is reserved for "submit / get feedback" and celebration.

### The universal contract (what makes new types additive)

Every runtime view, regardless of its UI, must honor one contract — so the host, route, data layer, and invalidation set never change when a view is added:

```ts
// components/task_runtime/contract.ts
export type TaskRuntimeView = React.ComponentType<{
  payload: TaskRuntimeViewModel;   // mapped from TaskRuntimeDto
  attempt: AttemptController;       // .complete(body) + status; attempt created/resumed by getTaskRuntime
}>;
```

A view consumes the payload, drives `attempt.complete(body)` with whatever completion body its type needs (a voice view posts the transcript + optional audio metadata from `tasks_trimmed.md`; a breathing view might post `{ held_seconds: 60 }`), and on success the standard invalidation set runs (plan / progress / freeLimit / entitlement). The backend creates or resumes the attempt inside `getTaskRuntime`, so a voice view starts in `Respond`-ready state; `stage_responses` stay optional in v1.

### Adding a new task type

| Case | Example | What changes |
|------|---------|--------------|
| **1. Same shape as an existing family** | another voice prompt exercise | A `tasks` row (content). No frontend code. |
| **2. New UI, same lifecycle** (start → one capture → complete+evaluate) | a different prompt layout, a text-input variant | New `ui_schema_key` + new view (its own or a new family shell) + one registry line. Host, routing, data layer, and invalidation unchanged. |
| **3. New UI *and* new lifecycle** (passive, multi-round, or no scoring) | Box breathing, Power pose, a multi-round game | Case 2 **plus** widen the shared contract: make `TaskRuntimeDto` and the completion request a **discriminated union by task type**, and keep `AttemptController.complete(body)` generic over the body. This is the only case that touches shared contracts. |

Backend alignment: `tasks_trimmed.md` already separates `ui_schema_key` (frontend shape) from `runtime_engine_key` (backend behavior); the voice trio shares `runtime_engine_key = voice_prompt_v1`. A fundamentally different type gets a **new value for both** keys. The frontend registry keys off `ui_schema_key`, and `task_attempts.completion_metadata` is generic `jsonb`, so a non-voice completion needs no migration — the schema is already friendly to case 3.

## Key Flow Designs

### Onboarding (guest-first, six steps)

```text
0 ensure guest session (SecureStore + create_guest_session) — precondition, no login required
1 selectTrigger -> saveTrigger -> backend assigns first task
2 open first-task runtime (calm; text-first, no confetti)
3 on first win -> variable reward (loud celebration, style label, rewrite, badge)
4 login step ("Save your Day 1 streak?") -> Apple/Google/Not now;
    on sign-in -> linkAccount (merge guest progress)
5 reminder step -> pick time -> THEN request OS notification permission -> saveReminder
6 land on Today's Plan preview (first task done, clear Next up) -> enter /app
   resume: if the user leaves mid-flow, re-enter at onboarding_state.current_step
```

### Start / complete a task

```text
tap item -> useFreeLimit.check()
  if blocked (non-subscriber at limit):
     show gentle banner + open paywall sheet ("that's your 3 free practices — streak's safe")
  else:
     getTaskRuntime(taskId) -> push /task/:taskId
     run phase machine -> submit completion
     optimistic: mark plan item current/done; on success invalidate plan/progress/freeLimit
     celebrate only on completion
```

### Paywall purchase / restore

```text
open paywall (limit trigger OR profile entry) -> render live RevenueCat offerings
  Annual ($rc_annual, pre-selected) / Monthly ($rc_monthly) + trial line + Restore
purchasePackage | restorePurchases -> refresh entitlement -> invalidate entitlement + freeLimit
always offer "Maybe later" (no dark patterns)
```

### Guest → authenticated linking

```text
signIn (Supabase Apple/Google) -> obtain auth session
  -> linkAccount(app_user_id, auth) on backend (merges guest progress)
  -> persist identity via SecureStore
  -> invalidate session/progress/entitlement/freeLimit
```

## Cross-Cutting UX

- **Data-backed screens** always render explicit Loading / Empty / Error via `StateViews`; query hooks expose these states directly.
- **Reduced motion**: `Celebration` and glow honor the OS reduced-motion preference (`lib/reduced_motion.ts`); gate confetti behind it.
- **Theme**: applied globally via Ionic CSS variables and `theme/tokens.ts` (Light & Warm: warm surfaces, orange CTA/celebration, blue primary/active); rounded ~2px-stroke icons; 12px radius token.
- **Feature flags**: future/unavailable areas (Role play) render disabled with a "Soon" badge, gated through `AnalyticsGateway`.
- **Analytics**: events are emitted from feature hooks (one seam), never scattered through components.
- **Privacy reassurance**: surfaced wherever the user is asked to produce content (first practice, recording).
- **Error boundaries**: each route is wrapped so a render failure degrades to a recoverable screen, not a blank app.
- **Safe areas / OS back**: handled by the Ionic shell and Capacitor, not per screen.

## Composition Root

`app/providers.tsx` is the client analog of the backend `composition/container.py`: it constructs the query client, theme, and the concrete adapter implementations, and provides them via context so features depend on ports only.

```ts
export function AppProviders({ children }: { children: React.ReactNode }) {
  const secureStore = new CapacitorSecureStore();
  const auth = new SupabaseAuthGateway(secureStore);
  const subscriptions = new RevenueCatSubscriptionGateway();
  const analytics = new PostHogAnalyticsGateway();
  const device = new CapacitorDeviceServices();

  const http = createHttpClient({ auth, secureStore });
  // STT provider swap (Deepgram -> Whisper-style) is a one-line change here, behind the port.
  // The adapter fetches its live-path credential from the backend; it holds no static key.
  const transcription = new DeepgramTranscriptionGateway({ http });
  const queryClient = createQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <IntegrationsProvider value={{ auth, subscriptions, analytics, device, secureStore, transcription, http }}>
        <ThemeProvider>{children}</ThemeProvider>
      </IntegrationsProvider>
    </QueryClientProvider>
  );
}
```

Swapping a vendor (e.g. RevenueCat → another provider, Supabase auth → another IdP, or Deepgram → a Whisper-style STT) is a change to one adapter and this wiring, not to screens or hooks.

## Why This Structure

- Keeps vendor-specific code centralized behind ports, mirroring the backend's repository/integration split.
- Makes future vendor replacement possible (auth, subscriptions, analytics, native) with localized change.
- Keeps view logic testable without a network or SDK, since hooks depend on injected ports and a mockable data layer.
- Avoids pushing data-fetching or business rules into Ionic pages.
- Renders new exercises as data through one shared `ui_schema_key` registry, matching the backend's task-type model so adding a task is content, not a screen.
- Separates server state (cache + invalidation) from UI state from durable identity, which is where most client bugs otherwise hide.

## Practical Caution

Do not over-abstract. Not every component needs a port, and not every value needs a global store. Wrap a vendor SDK behind a port only where the app realistically might swap it or needs it mocked (auth, subscriptions, analytics, native, transport); keep purely presentational pieces as plain components. Prefer feature hooks that expose exactly what a screen needs over a generic "view-model framework." Keep server data in the query cache rather than mirroring it into stores, so there is one source of truth per resource.

## Out Of Scope For This Pass

- Exact component trees, styling specifics, and animation timings (deferred to `tasks_trimmed.md` runtime contracts and design QA).
- Exact API route names and payloads (owned by backend; consumed here via the data layer).
- Role play screens and behavior (future, flag-gated).
- Detailed analytics event taxonomy.
- Offline/sync strategy beyond basic resume behavior.
