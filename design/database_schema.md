# i-am-witty Database Schema

Source: `functional_requirements.md`

Target backend: Supabase + Postgres, with RevenueCat for subscriptions and PostHog for analytics/feature flags.

## Design Principles

- Use one durable app identity table, `app_users`, for both guest and authenticated users.
- Reference Supabase `auth.users` only after a user signs in.
- Keep tasks generic. A task has metadata and a type, but task-specific interaction behavior is not modeled here.
- Store user-specific daily plans as plan instances, not only derived views, so progress can resume reliably.
- Treat RevenueCat as the source of subscription truth, while keeping a local entitlement mirror for access checks.
- Treat PostHog as the source for analytics/session replay/feature flags, while keeping only local config or overrides that the backend must enforce.

## Entity Overview

Core user data:
- `app_users`: Central app-level identity record for both guest and authenticated users.
- `guest_sessions`: Anonymous session tracking before the user creates or links an account.
- `user_profiles`: User-facing profile fields shown in the app.
- `user_progress_summaries`: Cached progress counters for fast Home and Profile reads.

Onboarding:
- `onboarding_states`: Resumable onboarding state and personalization choices.
- `onboarding_trigger_task_mappings`: Mapping from onboarding trigger choices to candidate first tasks.

Tasks and plans:
- `task_types`: High-level categories/types that tasks belong to.
- `tasks`: Reusable catalog of tasks available across onboarding, daily plans, and Practice.
- `daily_plans`: A user's generated daily plan for a specific local date.
- `daily_plan_items`: Ordered task items inside a user's daily plan.
- `task_attempts`: Records of each time a user starts, completes, or abandons a task.
- `user_day_activity`: Per-day activity facts used for the weekly strip and streak calculations.

Limits and subscriptions:
- `daily_usage_counters`: Per-day free task usage for enforcing non-subscriber limits.
- `revenuecat_customers`: Links app users to their RevenueCat customer identity.
- `subscription_entitlements`: Local mirror of RevenueCat entitlement state for backend access checks.
- `revenuecat_events`: RevenueCat webhook events for idempotency, audit, and entitlement sync.

Reminders and devices:
- `reminder_preferences`: User's selected reminder preference and scheduling state.
- `notification_devices`: User device and push notification delivery state.

Support and configuration:
- `support_messages`: Support messages submitted through the in-app chat entry point.
- `app_config`: Configurable app values and public links used by the client/backend.
- `feature_gate_defaults`: Backend-enforced feature gate defaults and entitlement requirements.
- `app_release_channels`: Release-channel and app-version metadata relevant to backend rollout decisions.

## Enums

```sql
create type user_status as enum ('guest', 'active', 'disabled', 'deleted');
create type onboarding_step as enum (
  'trigger_question',
  'first_task',
  'first_win',
  'account_prompt',
  'reminder_prompt',
  'complete'
);
create type onboarding_trigger as enum (
  'group_chats',
  'dates',
  'work',
  'friends',
  'stage',
  'teased'
);
create type task_access_tier as enum ('free', 'premium');
create type task_status as enum ('active', 'inactive', 'future');
create type daily_plan_status as enum ('active', 'completed', 'expired');
create type daily_plan_item_status as enum ('upcoming', 'current', 'completed', 'missed', 'skipped');
create type task_attempt_source as enum ('onboarding', 'daily_plan', 'practice_library', 'role_play');
create type task_attempt_status as enum ('started', 'completed', 'abandoned');
create type subscription_status as enum ('active', 'trialing', 'past_due', 'canceled', 'expired', 'unknown');
create type reminder_status as enum ('enabled', 'skipped', 'disabled');
create type notification_permission_status as enum ('unknown', 'granted', 'denied', 'provisional');
create type support_message_status as enum ('received', 'delivered', 'failed', 'closed');
```

## Tables

The snippets below describe the intended schema. Where tables reference each other cyclically or reference tables shown later, create the column first and add the foreign key constraint after both tables exist.

### app_users

Durable user identity used by all app tables.

```sql
create table app_users (
  id uuid primary key default gen_random_uuid(),
  auth_user_id uuid unique references auth.users(id) on delete set null,
  status user_status not null default 'guest',
  timezone text not null default 'UTC',
  locale text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  last_seen_at timestamptz,
  deleted_at timestamptz
);
```

Notes:
- Guest users have `auth_user_id = null`.
- On login, the guest `app_users` row is linked to the Supabase `auth.users.id`.

### guest_sessions

Tracks unauthenticated sessions before account creation.

```sql
create table guest_sessions (
  id uuid primary key default gen_random_uuid(),
  app_user_id uuid not null references app_users(id) on delete cascade,
  session_token_hash text not null unique,
  created_at timestamptz not null default now(),
  last_seen_at timestamptz,
  expires_at timestamptz,
  converted_at timestamptz,
  metadata jsonb not null default '{}'::jsonb
);
```

### user_profiles

Profile data rendered in the Profile screen.

```sql
create table user_profiles (
  app_user_id uuid primary key references app_users(id) on delete cascade,
  display_name text,
  avatar_key text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### user_progress_summaries

Cached progress counters for fast profile/home reads.

```sql
create table user_progress_summaries (
  app_user_id uuid primary key references app_users(id) on delete cascade,
  completed_task_count integer not null default 0 check (completed_task_count >= 0),
  current_streak_count integer not null default 0 check (current_streak_count >= 0),
  longest_streak_count integer not null default 0 check (longest_streak_count >= 0),
  last_activity_date date,
  last_qualified_streak_date date,
  streak_freezes_available integer not null default 0 check (streak_freezes_available >= 0),
  updated_at timestamptz not null default now()
);
```

### onboarding_states

Stores resumable onboarding progress.

```sql
create table onboarding_states (
  app_user_id uuid primary key references app_users(id) on delete cascade,
  current_step onboarding_step not null default 'trigger_question',
  selected_trigger onboarding_trigger,
  first_task_id uuid,
  first_task_attempt_id uuid,
  first_win_at timestamptz,
  account_prompt_seen_at timestamptz,
  reminder_prompt_seen_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Add these foreign keys after `tasks` and `task_attempts` exist:

```sql
alter table onboarding_states
  add constraint onboarding_states_first_task_fk
  foreign key (first_task_id)
  references tasks(id)
  on delete set null;

alter table onboarding_states
  add constraint onboarding_states_first_task_attempt_fk
  foreign key (first_task_attempt_id)
  references task_attempts(id)
  on delete set null;
```

### task_types

Defines high-level task types without defining task behavior.

```sql
create table task_types (
  id text primary key,
  display_name text not null,
  description text,
  is_active boolean not null default true,
  sort_order integer not null default 0,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Seed examples:
- `sprint`
- `improv`
- `calm`
- `story`

### tasks

Catalog of tasks available to onboarding, daily plans, and the Practice screen.

```sql
create table tasks (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  task_type_id text not null references task_types(id),
  duration_seconds integer check (duration_seconds > 0),
  thumbnail_key text,
  access_tier task_access_tier not null default 'free',
  status task_status not null default 'active',
  sort_order integer not null default 0,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Seed examples:
- `warm-up-riff`
- `yes-and`
- `box-breathing`
- `peak-end-hook`
- `one-word-story`
- `punch-it-up`
- `sixty-second-story`
- `power-pose`

### onboarding_trigger_task_mappings

Maps onboarding trigger choices to first tasks.

```sql
create table onboarding_trigger_task_mappings (
  id uuid primary key default gen_random_uuid(),
  trigger onboarding_trigger not null,
  task_id uuid not null references tasks(id) on delete cascade,
  priority integer not null default 100,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (trigger, task_id)
);
```

### daily_plans

One daily plan per user per local day.

```sql
create table daily_plans (
  id uuid primary key default gen_random_uuid(),
  app_user_id uuid not null references app_users(id) on delete cascade,
  plan_date date not null,
  timezone text not null,
  status daily_plan_status not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (app_user_id, plan_date)
);
```

### daily_plan_items

Ordered task instances inside a daily plan.

```sql
create table daily_plan_items (
  id uuid primary key default gen_random_uuid(),
  daily_plan_id uuid not null references daily_plans(id) on delete cascade,
  task_id uuid not null references tasks(id),
  position integer not null check (position > 0),
  status daily_plan_item_status not null default 'upcoming',
  current_attempt_id uuid,
  started_at timestamptz,
  completed_at timestamptz,
  missed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (daily_plan_id, position)
);
```

Recommended constraint:

```sql
create unique index one_current_item_per_plan
  on daily_plan_items (daily_plan_id)
  where status = 'current';
```

### task_attempts

Records task starts and completions. Detailed task behavior stays outside this schema pass.

```sql
create table task_attempts (
  id uuid primary key default gen_random_uuid(),
  app_user_id uuid not null references app_users(id) on delete cascade,
  task_id uuid not null references tasks(id),
  daily_plan_item_id uuid references daily_plan_items(id) on delete set null,
  source task_attempt_source not null,
  status task_attempt_status not null default 'started',
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  abandoned_at timestamptz,
  completion_metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Then add the reverse reference after both tables exist:

```sql
alter table daily_plan_items
  add constraint daily_plan_items_current_attempt_fk
  foreign key (current_attempt_id)
  references task_attempts(id)
  on delete set null;
```

### user_day_activity

Supports the weekly activity strip and streak calculation inputs.

```sql
create table user_day_activity (
  app_user_id uuid not null references app_users(id) on delete cascade,
  activity_date date not null,
  timezone text not null,
  completed_task_count integer not null default 0 check (completed_task_count >= 0),
  had_missed_plan_items boolean not null default false,
  streak_qualified boolean not null default false,
  streak_protected boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (app_user_id, activity_date)
);
```

### daily_usage_counters

Tracks free daily task usage for non-subscribers.

```sql
create table daily_usage_counters (
  app_user_id uuid not null references app_users(id) on delete cascade,
  usage_date date not null,
  timezone text not null,
  free_tasks_completed integer not null default 0 check (free_tasks_completed >= 0),
  free_task_limit integer not null default 3 check (free_task_limit >= 0),
  paywall_shown_at timestamptz,
  updated_at timestamptz not null default now(),
  primary key (app_user_id, usage_date)
);
```

### revenuecat_customers

Maps app users to RevenueCat customer identifiers.

```sql
create table revenuecat_customers (
  app_user_id uuid primary key references app_users(id) on delete cascade,
  revenuecat_app_user_id text not null unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### subscription_entitlements

Local mirror of RevenueCat entitlement state for access decisions.

```sql
create table subscription_entitlements (
  id uuid primary key default gen_random_uuid(),
  app_user_id uuid not null references app_users(id) on delete cascade,
  entitlement_key text not null,
  status subscription_status not null default 'unknown',
  product_id text,
  period_type text,
  current_period_started_at timestamptz,
  current_period_ends_at timestamptz,
  trial_ends_at timestamptz,
  revoked_at timestamptz,
  last_synced_at timestamptz not null default now(),
  raw_snapshot jsonb not null default '{}'::jsonb,
  unique (app_user_id, entitlement_key)
);
```

### revenuecat_events

Stores webhook events for idempotency and audit.

```sql
create table revenuecat_events (
  id uuid primary key default gen_random_uuid(),
  revenuecat_event_id text not null unique,
  app_user_id uuid references app_users(id) on delete set null,
  event_type text not null,
  entitlement_key text,
  product_id text,
  purchased_at timestamptz,
  expires_at timestamptz,
  payload jsonb not null,
  received_at timestamptz not null default now(),
  processed_at timestamptz
);
```

### reminder_preferences

Stores the user's daily warm-up reminder choice.

```sql
create table reminder_preferences (
  app_user_id uuid primary key references app_users(id) on delete cascade,
  status reminder_status not null default 'skipped',
  timing_key text,
  local_time time,
  timezone text not null default 'UTC',
  last_scheduled_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Expected `timing_key` values:
- `before_work`
- `before_going_out`
- `after_dinner`
- `fixed_2000`

### notification_devices

Stores device and push-delivery state.

```sql
create table notification_devices (
  id uuid primary key default gen_random_uuid(),
  app_user_id uuid not null references app_users(id) on delete cascade,
  device_key text not null,
  platform text not null,
  push_token text,
  permission_status notification_permission_status not null default 'unknown',
  app_version text,
  release_channel text,
  last_seen_at timestamptz,
  disabled_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (app_user_id, device_key)
);
```

### support_messages

Stores user-submitted support messages.

```sql
create table support_messages (
  id uuid primary key default gen_random_uuid(),
  app_user_id uuid references app_users(id) on delete set null,
  guest_session_id uuid references guest_sessions(id) on delete set null,
  source_screen text,
  message_text text not null,
  status support_message_status not null default 'received',
  routed_to text,
  external_ticket_id text,
  delivery_error text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  delivered_at timestamptz,
  closed_at timestamptz
);
```

### app_config

Public or server-side app configuration, including external links.

```sql
create table app_config (
  key text primary key,
  value jsonb not null,
  is_public boolean not null default false,
  description text,
  updated_at timestamptz not null default now()
);
```

Seed examples:
- `telegram_community_url`
- `terms_url`
- `privacy_url`
- `free_task_limit`

### feature_gate_defaults

Local defaults/overrides for backend-enforced feature gates. PostHog remains the feature flag source for product experimentation.

```sql
create table feature_gate_defaults (
  feature_key text primary key,
  default_enabled boolean not null default false,
  requires_entitlement text,
  min_app_version text,
  metadata jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
```

Seed examples:
- `role_play`
- `witty_plus`
- `premium_task_library`

### app_release_channels

Captures app-version or Capgo-channel rules only where backend behavior depends on rollout state.

```sql
create table app_release_channels (
  channel_key text primary key,
  min_supported_version text,
  latest_version text,
  is_active boolean not null default true,
  metadata jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
```

## Key Relationships

- `app_users.auth_user_id` optionally links to `auth.users.id`.
- `guest_sessions.app_user_id` links guest sessions to a durable app user.
- `user_profiles`, `user_progress_summaries`, `onboarding_states`, `reminder_preferences`, and `revenuecat_customers` are one-to-one with `app_users`.
- `tasks.task_type_id` links each task to a generic task type.
- `onboarding_trigger_task_mappings` maps onboarding triggers to first-task candidates.
- `daily_plans` has many `daily_plan_items`.
- `daily_plan_items.task_id` points to the catalog task.
- `task_attempts` records task activity from onboarding, daily plans, or the Practice screen.
- `user_day_activity` and `daily_usage_counters` are per-user, per-local-day records.
- `subscription_entitlements` mirrors RevenueCat access state for backend decisions.

## Recommended Indexes

```sql
create index app_users_auth_user_id_idx on app_users (auth_user_id);
create index guest_sessions_app_user_id_idx on guest_sessions (app_user_id);

create index tasks_status_sort_idx on tasks (status, sort_order);
create index tasks_type_idx on tasks (task_type_id);

create index daily_plans_user_date_idx on daily_plans (app_user_id, plan_date desc);
create index daily_plan_items_plan_status_idx on daily_plan_items (daily_plan_id, status, position);

create index task_attempts_user_started_idx on task_attempts (app_user_id, started_at desc);
create index task_attempts_user_task_idx on task_attempts (app_user_id, task_id);
create index task_attempts_plan_item_idx on task_attempts (daily_plan_item_id);

create index user_day_activity_user_date_idx on user_day_activity (app_user_id, activity_date desc);
create index subscription_entitlements_user_status_idx on subscription_entitlements (app_user_id, status);
create index revenuecat_events_app_user_idx on revenuecat_events (app_user_id);
create index notification_devices_user_idx on notification_devices (app_user_id);
create index support_messages_status_created_idx on support_messages (status, created_at);
```

## RLS And Access Model

Recommended Supabase policy direction:

- Authenticated users may read their own rows where `app_users.auth_user_id = auth.uid()`.
- Authenticated users may update limited profile/reminder fields on their own user.
- Guest operations should go through Edge Functions or backend APIs that validate `guest_sessions.session_token_hash`; avoid broad anonymous table writes.
- Task catalog and public `app_config` can be readable by anon/authenticated clients.
- Task catalog writes, entitlement writes, RevenueCat event writes, support routing, and progress/streak mutations should use service-role backend code.
- Subscription tables should expose only summarized entitlement state to clients, not raw webhook payloads.
- Support message creation should be API-mediated to enforce rate limits and delivery routing.

## API-Oriented Operations This Schema Supports

- Create guest session.
- Link guest app user to Supabase auth user.
- Read or update profile.
- Save onboarding trigger.
- Assign first onboarding task.
- Get Practice task catalog.
- Get or create today's plan.
- Start task attempt.
- Complete task attempt.
- Compute home/progress summary.
- Check free limit and entitlement before starting a task.
- Refresh RevenueCat entitlement state.
- Save reminder preference.
- Register notification device.
- Submit support message.
- Read public app configuration.

## MVP Build Order

1. `app_users`, `guest_sessions`, `user_profiles`, `user_progress_summaries`
2. `task_types`, `tasks`, `onboarding_states`, `onboarding_trigger_task_mappings`
3. `daily_plans`, `daily_plan_items`, `task_attempts`, `user_day_activity`
4. `daily_usage_counters`, `revenuecat_customers`, `subscription_entitlements`, `revenuecat_events`
5. `reminder_preferences`, `notification_devices`
6. `support_messages`, `app_config`, `feature_gate_defaults`, `app_release_channels`

## Open Schema Questions

- Whether guest users should be represented through custom `guest_sessions` only or Supabase anonymous auth.
- Whether streak counters should be fully materialized in `user_progress_summaries` or computed from `user_day_activity`.
- Whether task type definitions need a separate config schema once task behavior is specified.
- Whether PostHog feature flag evaluations need to be cached locally for offline/backend-only decisions.
- Whether notification delivery will be handled by Supabase Edge Functions, a separate worker, or a third-party notification service.
