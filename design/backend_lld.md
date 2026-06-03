# i-am-witty Backend LLD

Source: `functional_requirements.md` and `database_schema.md`

## Goal

Define a Python backend code structure that keeps business logic independent from Supabase/Postgres details, while still fitting the current stack. Repositories live in one infrastructure area so the database implementation can be replaced later with limited changes.

## Architectural Style

Use a ports-and-adapters structure:

```text
API / Python function or route handler
  -> Application Service
    -> Domain Policies
    -> Repository Ports
    -> Integration Ports
  -> Infrastructure Implementations
```

Application services depend on Python protocols, not directly on Supabase clients.

## Suggested Directory Structure

```text
backend/
  functions/
    create_guest_session.py
    link_auth_user.py
    update_onboarding.py
    get_home.py
    get_practice_catalog.py
    start_task.py
    complete_task.py
    save_reminder.py
    submit_support.py
    revenue_cat_webhook.py

  shared/
    application/
      identity_service.py
      onboarding_service.py
      task_catalog_service.py
      daily_plan_service.py
      task_attempt_service.py
      progress_service.py
      entitlement_service.py
      reminder_service.py
      support_service.py
      app_config_service.py

    domain/
      models/
        app_user.py
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
        subscription_provider.py
        analytics.py

    infrastructure/
      db/
        supabase_client.py
        transaction.py
        rpc.py
        sql/
          complete_task_attempt.sql
          link_guest_user.sql
      repositories/
        supabase_user_repository.py
        supabase_guest_session_repository.py
        supabase_profile_repository.py
        supabase_onboarding_repository.py
        supabase_task_repository.py
        supabase_daily_plan_repository.py
        supabase_task_attempt_repository.py
        supabase_progress_repository.py
        supabase_usage_repository.py
        supabase_entitlement_repository.py
        supabase_reminder_repository.py
        supabase_notification_device_repository.py
        supabase_support_repository.py
        supabase_config_repository.py
      integrations/
        revenue_cat_client.py
        posthog_client.py

    composition/
      container.py

    errors/
      app_error.py
      http_errors.py
```

## Layer Responsibilities

### Functions

Python function or route-handler entry points. They should parse HTTP input, authenticate or resolve guest sessions, call application services, and return API responses.

They should not contain business rules or direct database queries.

### Application Services

Use-case orchestration layer. Services coordinate repositories, policies, transactions, and integrations.

Examples:
- `TaskAttemptService.start_task`
- `TaskAttemptService.complete_task`
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

Python `Protocol` interfaces used by services. Ports describe what the application needs, not how Supabase implements it.

### Infrastructure

Concrete implementations of repository and integration ports. Supabase-specific query code lives here.

If the database changes later, replace the repository implementations in `infrastructure/repositories/*` with new implementations while keeping application services largely unchanged.

### Postgres-Specific Logic

Postgres-specific logic should stay inside infrastructure, not application services.

Use this split:
- `infrastructure/repositories/*.py`: Supabase/Postgres query code for normal reads and writes.
- `infrastructure/db/transaction.py`: transaction helpers and transaction boundary utilities.
- `infrastructure/db/rpc.py`: wrappers for calling Postgres RPC functions.
- `infrastructure/db/sql/*.sql`: SQL bodies for high-integrity database functions that must run atomically.
- migrations, if used by the project tooling: table definitions, indexes, constraints, triggers, and seed data.

Application services should call repository or RPC wrapper methods instead of embedding SQL.

Example:

```text
TaskAttemptService.complete_task
  -> TaskAttemptRepository.complete_attempt
  -> ProgressRepository.update_after_completion
  -> UsageRepository.increment_daily_usage
```

For a highly atomic operation, the service can call a single repository/RPC wrapper:

```text
TaskAttemptService.complete_task
  -> TaskAttemptRepository.complete_task_transactionally
  -> infrastructure/db/sql/complete_task_attempt.sql
```

This keeps Postgres replaceable at the service layer while still allowing Postgres to enforce critical consistency where needed.

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

Implementation options:
- Use a transaction helper if the Supabase runtime supports it cleanly.
- Use Postgres RPC functions for high-integrity atomic operations.
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

`composition/container.py` wires services to concrete implementations.

Example:

```python
def create_container() -> Container:
    db = create_supabase_client()

    task_repository = SupabaseTaskRepository(db)
    attempt_repository = SupabaseTaskAttemptRepository(db)
    daily_plan_repository = SupabaseDailyPlanRepository(db)
    progress_repository = SupabaseProgressRepository(db)
    usage_repository = SupabaseUsageRepository(db)
    entitlement_repository = SupabaseEntitlementRepository(db)

    return Container(
        task_attempt_service=TaskAttemptService(
            attempts=attempt_repository,
            tasks=task_repository,
            daily_plans=daily_plan_repository,
            progress=progress_repository,
            usage=usage_repository,
            entitlements=entitlement_repository,
        )
    )
```

## Why This Structure

- Keeps Supabase-specific code centralized.
- Makes future database replacement possible.
- Keeps business rules testable without a database.
- Avoids pushing business logic into HTTP/function handlers.
- Supports additive complexity for future task types without rewriting the core task model.

## Practical Caution

Do not over-abstract every table into generic CRUD. Repositories should expose operations the application actually needs. This keeps services readable and prevents the repository layer from becoming a thin, noisy wrapper around SQL.
