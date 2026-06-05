# i-am-witty Backend LLD

Source: `backend_functional_requirements.md`, `database_schema.md`, and `tasks_trimmed.md`

## Goal

Define a Python (FastAPI on Cloud Run) backend code structure that keeps business logic independent from Neon Postgres details, while still fitting the current stack. Repositories live in one infrastructure area so the database implementation can be replaced later with limited changes.

## Architectural Style

Use a ports-and-adapters structure:

```text
FastAPI route handler (Cloud Run)
  -> Application Service
    -> Domain Policies
    -> Repository Ports
    -> Integration Ports
  -> Infrastructure Implementations
```

Application services depend on Python protocols, not directly on the Neon Postgres driver or other vendor SDKs.

## Suggested Directory Structure

```text
backend/
  app/                                 # single Python package; imports namespaced as app.<layer>.*
    api/                               # inbound adapter: FastAPI app deployed to Cloud Run
      main.py                          # ASGI app factory; mounts routers, middleware, container
      deps.py                          # FastAPI dependencies: Firebase ID-token auth, guest-session resolution, container access
      routes/
        create_guest_session.py
        link_auth_user.py
        update_onboarding.py
        get_home.py
        get_practice_catalog.py
        get_task_runtime.py
        start_task.py
        complete_task.py
        save_reminder.py
        register_notification_device.py
        submit_support.py
        revenue_cat_webhook.py
        create_transcription_token.py  # mints a short-lived STT credential for the client live path

    application/
      identity_service.py
      onboarding_service.py
      task_catalog_service.py
      task_runtime_service.py
      daily_plan_service.py
      task_attempt_service.py
      progress_service.py
      entitlement_service.py
      reminder_service.py
      support_service.py
      app_config_service.py
      transcription_service.py

    domain/
      models/
        app_user.py
        task_type.py
        task.py
        daily_plan.py
        task_attempt.py
        entitlement.py
      policies/
        daily_limit_policy.py
        streak_policy.py
        task_access_policy.py

    ports/
      repositories/
        user_repository.py
        guest_session_repository.py
        profile_repository.py
        onboarding_repository.py
        task_repository.py
        daily_plan_repository.py
        task_attempt_repository.py
        progress_repository.py
        usage_repository.py
        entitlement_repository.py
        reminder_repository.py
        notification_device_repository.py
        support_repository.py
        config_repository.py
      integrations/
        auth_token_verifier.py
        subscription_provider.py
        analytics.py
        transcription_provider.py
      task_runtime_engine.py

    infrastructure/
      db/
        engine.py                          # SQLAlchemy async engine + async_sessionmaker (Neon/Postgres)
        session.py                         # per-request AsyncSession provider + unit-of-work / transaction scope
        orm/                               # SQLAlchemy declarative models (mapped tables); distinct from domain models
          base.py                          # DeclarativeBase + MetaData (the Alembic autogenerate target)
          users.py                         # app_users, guest_sessions, user_profiles, user_progress_summaries
          onboarding.py                    # onboarding_states, onboarding_trigger_task_mappings
          tasks.py                         # task_types, tasks
          plans.py                         # daily_plans, daily_plan_items, task_attempts, user_day_activity
          billing.py                       # daily_usage_counters, revenuecat_*, subscription_entitlements
          comms.py                         # reminder_preferences, notification_devices, support_messages
          config.py                        # app_config, feature_gate_defaults, app_release_channels
        sql_functions.py                   # high-integrity stored-function calls via session.execute(text(...))
        sql/
          complete_task_attempt.sql
          link_guest_user.sql
      repositories/
        pg_user_repository.py              # SQLAlchemy ORM impl; maps ORM rows <-> domain models
        pg_guest_session_repository.py
        pg_profile_repository.py
        pg_onboarding_repository.py
        pg_task_repository.py
        pg_daily_plan_repository.py
        pg_task_attempt_repository.py
        pg_progress_repository.py
        pg_usage_repository.py
        pg_entitlement_repository.py
        pg_reminder_repository.py
        pg_notification_device_repository.py
        pg_support_repository.py
        pg_config_repository.py
      integrations/
        firebase_auth_verifier.py          # verifies Firebase ID tokens (Firebase Admin SDK)
        revenue_cat_client.py
        posthog_client.py
        deepgram_transcription_client.py   # swappable for a whisper_transcription_client.py
      task_engines.py

    composition/
      container.py

    errors/
      app_error.py
      http_errors.py

  alembic/                                 # migrations, autogenerated from app.infrastructure.db.orm metadata
    env.py
    versions/
  alembic.ini
```

## Layer Responsibilities

### API (FastAPI Routes)

FastAPI route handlers, served by a single ASGI app on Cloud Run (`api/main.py`). They parse HTTP input, authenticate the request (verify the Firebase ID token via the auth dependency) or resolve a guest session, call application services, and return API responses. Cross-cutting concerns — Firebase token verification, guest-session resolution, and access to the composition container — are provided as FastAPI dependencies in `api/deps.py`.

They should not contain business rules or direct database queries.

### Application Services

Use-case orchestration layer. Services coordinate repositories, policies, transactions, and integrations.

Examples:
- `TaskAttemptService.start_task`
- `TaskAttemptService.complete_task`
- `TaskRuntimeService.get_task_runtime`
- `DailyPlanService.get_or_create_today_plan`
- `OnboardingService.save_trigger_and_assign_first_task`
- `EntitlementService.sync_revenue_cat_event`

### Domain Models And Policies

Small pure Python objects/functions for decisions that should not know about the database.

Examples:
- Can this user start another free task today?
- Does this task require Witty+?
- Does this completed task qualify the user for streak progress?

### Ports

Python `Protocol` interfaces used by services. Ports describe what the application needs, not how Neon/Postgres implements it.

### Infrastructure

Concrete implementations of repository and integration ports. Neon/Postgres-specific query code lives here. Persistence uses the SQLAlchemy ORM: declarative models live in `infrastructure/db/orm/` and are mapped to the schema in `database_schema.md`.

If the database changes later, replace the repository implementations in `infrastructure/repositories/*` with new implementations while keeping application services largely unchanged.

### Postgres-Specific Logic

Postgres-specific logic should stay inside infrastructure, not application services.

Use this split:
- `infrastructure/db/orm/*.py`: SQLAlchemy declarative models — the mapped tables — kept separate from `domain/models`.
- `infrastructure/repositories/*.py`: SQLAlchemy ORM query code (over an `AsyncSession`) for normal reads and writes; each repository maps ORM rows to and from domain models.
- `infrastructure/db/engine.py` and `session.py`: the async engine/sessionmaker and the per-request `AsyncSession` that serves as the unit of work / transaction scope.
- `infrastructure/db/sql_functions.py`: wrappers that call high-integrity Postgres stored functions via `session.execute(text(...))`.
- `infrastructure/db/sql/*.sql`: SQL bodies for high-integrity database functions that must run atomically.
- `alembic/versions/*`: migrations, autogenerated from the ORM models' metadata, are the executable transcription of `database_schema.md`.

Application services should call repository or stored-function wrapper methods instead of embedding SQL.

Example:

```text
TaskAttemptService.complete_task
  -> TaskAttemptRepository.complete_attempt
  -> ProgressRepository.update_after_completion
  -> UsageRepository.increment_daily_usage
```

For a highly atomic operation, the service can call a single repository/stored-function wrapper:

```text
TaskAttemptService.complete_task
  -> TaskAttemptRepository.complete_task_transactionally
  -> infrastructure/db/sql/complete_task_attempt.sql
```

This keeps Postgres replaceable at the service layer while still allowing Postgres to enforce critical consistency where needed.

## ORM Models vs. Domain Models

These are two distinct layers and must not be collapsed into one:

- **ORM models** (`infrastructure/db/orm/*.py`): SQLAlchemy declarative classes mapped to the physical tables in `database_schema.md`. They carry columns, relationships, and persistence concerns, and their metadata is what Alembic autogenerates migrations from.
- **Domain models** (`domain/models/*.py`): small, persistence-ignorant Python objects that express business state and feed the policies. They import no SQLAlchemy and have no notion of tables, sessions, or columns.

Repositories are the only place the two meet: a repository loads ORM rows through the session and maps them into domain models on the way out, and maps domain input back to ORM writes on the way in. The ports in `ports/repositories` stay unchanged — they still speak in domain types — so the SQLAlchemy choice never leaks above `infrastructure/`.

Cost: this mapping is boilerplate. If it grows tiresome, the lighter alternative is SQLAlchemy's imperative (classical) mapping — map plain domain dataclasses to `Table` definitions without decorating them — which keeps the domain free of ORM syntax while removing the duplicate class. Prefer the explicit two-class split first; reach for imperative mapping only if the duplication becomes a real burden.

## Repository Design

Repositories should be grouped in one infrastructure area, but exposed through interfaces in `ports/repositories`.

Prefer business-oriented methods over generic CRUD. For example:

```python
from typing import Protocol

class DailyPlanRepository(Protocol):
    async def get_plan_with_items(self, app_user_id: str, plan_date: str) -> DailyPlan | None:
        ...

    async def create_plan_with_items(self, input: CreateDailyPlanInput) -> DailyPlan:
        ...

    async def mark_item_current(self, input: MarkPlanItemCurrentInput) -> None:
        ...

    async def mark_item_completed(self, input: MarkPlanItemCompletedInput) -> None:
        ...
```

Avoid forcing services to manually compose many low-level table calls when the operation is always used as a business unit.

## Example Repository Port

```python
from typing import Protocol

class TaskAttemptRepository(Protocol):
    async def create_started_attempt(self, input: CreateAttemptInput) -> TaskAttempt:
        ...

    async def complete_attempt(self, input: CompleteAttemptInput) -> TaskAttempt:
        ...

    async def abandon_attempt(self, input: AbandonAttemptInput) -> None:
        ...

    async def find_by_id(self, attempt_id: str) -> TaskAttempt | None:
        ...
```

## Example Service

```python
class TaskAttemptService:
    def __init__(
        self,
        attempts: TaskAttemptRepository,
        tasks: TaskRepository,
        daily_plans: DailyPlanRepository,
        progress: ProgressRepository,
        usage: UsageRepository,
        entitlements: EntitlementRepository,
    ) -> None:
        self.attempts = attempts
        self.tasks = tasks
        self.daily_plans = daily_plans
        self.progress = progress
        self.usage = usage
        self.entitlements = entitlements

    async def start_task(self, input: StartTaskInput) -> StartTaskResult:
        task = await self.tasks.find_available_by_id(input.task_id)
        entitlement = await self.entitlements.get_access_state(input.app_user_id)

        # Apply task access and daily free-limit policies here.

        attempt = await self.attempts.create_started_attempt(
            CreateAttemptInput(
                app_user_id=input.app_user_id,
                task_id=input.task_id,
                source=input.source,
                daily_plan_item_id=input.daily_plan_item_id,
            )
        )

        return StartTaskResult(attempt=attempt)
```

## Task Type UI And Runtime Config

Tasks of the same type should share the same client UI structure. The task type owns that structure through a `ui_schema_key`; each task owns the content and assets that fill that structure.

The current task type catalog, representative per-exercise config, generated payload contracts, and prompt/evaluation behavior are defined in `design/tasks_trimmed.md`. The LLD should implement those contracts rather than re-deriving task behavior from legacy prompt files.

Example:

```text
task_types
  id = voice_scaffolded_prompt
  ui_schema_key = voice_scaffolded_prompt_v1
  runtime_engine_key = voice_prompt_v1

tasks
  slug = push-pull
  task_type_id = voice_scaffolded_prompt
  title = Push/Pull
  thumbnail_key = ...
  image_key = ...
  content = {
    "prompt_label": "Scenario",
    "scaffold_stages": [...]
  }
  runtime_config = {
    "backend_key": "pushPull",
    "prompt_bundle_key": "push_pull_v1"
  }
```

The backend should expose enough data for the client to render the shared UI without hardcoding per-task copy or assets.

Recommended application service:

```text
TaskRuntimeService
  - loads task + task type
  - checks availability and entitlement
  - returns ui_schema_key and task content/assets
  - routes generation/completion to the right task engine when needed
```

Recommended port:

```python
from typing import Protocol

class TaskRuntimeEngine(Protocol):
    async def generate(self, input: GenerateTaskInput) -> GeneratedTaskPayload:
        ...

    async def complete(self, input: CompleteTaskRuntimeInput) -> TaskRuntimeResult:
        ...
```

Current voice exercises can be wrapped by one implementation:

```text
VoicePromptTaskEngine
  - supports task type ids from design/tasks_trimmed.md
  - uses runtime_config.backend_key such as "pushPull"
  - selects the prompt bundle/generator/evaluator from runtime_config
  - returns ui_schema_key-compatible payloads
```

The first implementation can adapt the current generator/evaluator behavior behind this engine, but `design/tasks_trimmed.md` is the contract. Task images and thumbnails are enough for the current catalog requirement.

## Speech-to-Text (STT) Provider

Voice tasks need a transcript, and the **backend is the authority** for the transcript that gets evaluated and stored. The provider (Deepgram today) is reached only through an integration port so it can be replaced later with a Whisper-style recognizer at the infrastructure layer — the same replaceability discipline applied to the Postgres repositories and the RevenueCat client. The provider API key lives only on the backend; it must never be shipped in the client bundle. This mirrors the frontend's "Client vs. backend split for speech-to-text" in `frontend_lld.md`.

The provider has two responsibilities, matching the client's two-path model:

- **Mint a short-lived credential** for the client's live-transcript path (the client streams directly to the provider for low latency, using this ephemeral token rather than a static key). Exposed via `create_transcription_token`.
- **Produce or confirm the authoritative final transcript** from the user's submitted answer audio on completion, before evaluation runs.

Port:

```python
from typing import Protocol

class TranscriptionProvider(Protocol):
    async def create_ephemeral_credential(self) -> EphemeralCredential:
        # short-lived, narrowly scoped; backend holds the real key
        ...

    async def transcribe(self, input: TranscribeInput) -> Transcript:
        # batch transcription of submitted answer audio; returns text + optional
        # prosody metadata (word/pause timings) when the provider supports it
        ...
```

Service:

```text
TranscriptionService
  - mint_live_credential()      -> used by create_transcription_token
  - resolve_final_transcript(submitted_transcript, answer_audio?) -> Transcript
      - when answer audio is present, the provider produces the authoritative transcript
      - otherwise the client-submitted transcript is accepted as-is
      - returns optional prosody metadata; callers must treat it as optional
```

Where it plugs into completion: `complete_task` (or the `VoicePromptTaskEngine.complete` path) calls `TranscriptionService.resolve_final_transcript` to obtain the authoritative transcript, then evaluates it. Both the STT call and the LLM evaluation are **external network calls and must run before/outside the database transaction** — never hold the `complete_task` transaction open across them (see Transaction Guidance).

Swappability notes:
- Deepgram→Whisper is an `infrastructure/integrations` swap plus the composition wiring; `TranscriptionProvider`, `TranscriptionService`, and `complete_task` are unchanged.
- A non-streaming provider can return an empty/no-op ephemeral credential; the client falls back to its text input and loses only the live transcript, not correctness.
- Evaluation must not depend on provider-specific signals (e.g. pause counts). Keep prosody fields optional in both the `Transcript` model and the evaluator, consistent with the optional `metadata` in the client `TranscriptionGateway`.

## Transaction Guidance

Mutations that update multiple tables should execute inside one transaction.

Examples:
- Completing a task attempt.
- Linking a guest user to an authenticated user.
- Processing a RevenueCat webhook.
- Creating a daily plan and its plan items.

For `complete_task`, the transaction should update:

```text
task_attempts
daily_plan_items
user_day_activity
user_progress_summaries
daily_usage_counters
onboarding_states, if onboarding task
```

External network calls in `complete_task` — resolving the authoritative transcript (`TranscriptionService`) and LLM evaluation (`VoicePromptTaskEngine.complete`) — must complete **before** this transaction opens. Do not hold a database transaction open across an STT or model call; compute the transcript and evaluation first, then perform the atomic multi-table write.

Implementation options:
- Use the SQLAlchemy `AsyncSession` as the unit of work: open one session per request and wrap a multi-table mutation in `async with session.begin()` so the writes commit or roll back together. All repositories in a request share that one session.
- Use Postgres stored functions (invoked through the session) for the highest-integrity atomic operations.
- Keep orchestration in Python, but avoid non-transactional multi-table writes for critical flows.

## Handling Future Intermediate Task State

Keep `task_attempts` as the parent attempt record.

When task types need persisted intermediate state, add child ports/repositories rather than changing the parent attempt shape:

```text
task_stage_definitions
task_attempt_stages
task_attempt_events
```

Example:

```text
task_attempts
  attempt_123, task = push_pull, status = started

task_attempt_stages
  attempt_123, stage 1, status = completed
  attempt_123, stage 2, status = completed
  attempt_123, stage 3, status = completed
```

This keeps scaffolded tasks like Push/Pull additive and avoids adding brittle columns such as `stage_1_transcript` or `stage_2_transcript`.

## Composition

`composition/container.py` wires services to concrete implementations. With the SQLAlchemy ORM there are **two scopes**: process-wide singletons built once at startup (engine, sessionmaker, stateless integration clients) and request-scoped services bound to a single `AsyncSession` so every repository in a request shares one unit of work.

Built once at startup (app lifespan):

```python
def create_app_container() -> AppContainer:
    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=5)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # Stateless integrations are safe to share across requests.
    auth_verifier = FirebaseAuthVerifier()
    # STT provider swap (Deepgram -> Whisper-style) is a one-line change here.
    transcription_service = TranscriptionService(DeepgramTranscriptionClient())

    return AppContainer(
        engine=engine,
        session_factory=session_factory,
        auth_token_verifier=auth_verifier,
        transcription_service=transcription_service,
    )
```

Built per request (in `api/deps.py`), bound to one `AsyncSession` so a multi-table write commits or rolls back as a unit:

```python
def build_request_services(session: AsyncSession, app: AppContainer) -> RequestServices:
    tasks = PgTaskRepository(session)
    attempts = PgTaskAttemptRepository(session)
    daily_plans = PgDailyPlanRepository(session)
    progress = PgProgressRepository(session)
    usage = PgUsageRepository(session)
    entitlements = PgEntitlementRepository(session)

    return RequestServices(
        task_attempt_service=TaskAttemptService(
            attempts=attempts,
            tasks=tasks,
            daily_plans=daily_plans,
            progress=progress,
            usage=usage,
            entitlements=entitlements,
        ),
    )
```

The FastAPI session dependency opens the `AsyncSession` (and its transaction scope) per request, builds the request services, and ensures commit/rollback and close at the end of the request.

## Why This Structure

- Keeps Postgres- and SQLAlchemy-specific code centralized in `infrastructure/`; ports and domain stay persistence-free.
- Makes future database replacement possible.
- Keeps business rules testable without a database.
- Avoids pushing business logic into HTTP route handlers.
- Supports additive complexity for future task types without rewriting the core task model.

## Hosting Portability / Future Self-Hosting

The target stack (FastAPI on Cloud Run + Neon Postgres) is deliberately portable to self-hosted Postgres and a self-hosted FastAPI process later. That migration is **low-code, moderate-ops**: it changes *where things run*, not *what the code does* — no business logic, schema, repository, or auth changes. Neon is wire-compatible Postgres reached via standard `asyncpg`/SQLAlchemy, so the DB move is mostly `DATABASE_URL` + data transfer (`pg_dump`/`pg_restore` or logical replication); FastAPI is a portable ASGI app, so the compute move is mostly packaging + deployment. What you take on by self-hosting is operational (TLS/reverse proxy, process supervision, autoscaling, backups/PITR, monitoring, public ingress for the `revenue_cat_webhook` endpoint), and no abstraction removes that burden.

Cost posture (why this is sequenced, not a conflict):
- At low/early scale, the managed stack is the **cheapest** option, not the expensive one: Cloud Run and Neon both **scale to zero**, so idle cost is ~$0. A self-hosted VM runs 24/7 at a fixed floor cost regardless of traffic.
- Self-hosting becomes the cost win only under **sustained, predictable traffic**, where a fixed VM amortizes better than per-request billing + managed-DB markup. Treat the move as a future optimization triggered by that crossover.
- The dominant cost driver for this backend is expected to be **per-task LLM evaluation + STT (Deepgram)**, not the web tier — focus cost effort there (model choice, caching, the free-task cap), not on hosting.
- Cloud Run tradeoff to decide: `min-instances=0` keeps cost near $0 but allows cold starts; `min-instances=1` removes cold starts but adds an always-on floor cost.

Keep the migration small by holding these constraints now:
- Talk to Postgres only over the standard wire protocol (`asyncpg`/SQLAlchemy) — never a Neon-proprietary serverless/HTTP driver — so `infrastructure/db/engine.py` is host-agnostic.
- Load all config (`DATABASE_URL`, secrets, port) from environment variables in one config module; never read config from a cloud-provider SDK inside services. Keep the container 12-factor (stateless, listens on `$PORT`, logs to stdout).
- If any cloud-proprietary service is adopted (e.g. Cloud Tasks/Scheduler for the notification-delivery open question, Pub/Sub, object storage), place it behind a `ports/integrations` port like every other vendor, so self-hosting swaps an adapter, not the services.
- Connection management: Cloud Run scales horizontally and each instance holds its own pool, which can exhaust Postgres `max_connections`. Keep a small per-instance pool, raise request concurrency (fewer instances for the same load = lower cost), and use a pooled (PgBouncer-style) endpoint. This same configuration carries over to a self-hosted PgBouncer unchanged.

## Practical Caution

Do not over-abstract every table into generic CRUD. Repositories should expose operations the application actually needs. This keeps services readable and prevents the repository layer from becoming a thin, noisy wrapper around SQL.
