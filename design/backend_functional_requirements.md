# i-am-witty Backend Functional Requirements

Source: `ux_existing` mockups and README, with task runtime behavior from `design/tasks_trimmed.md`.

## Scope

These requirements describe the backend capabilities needed to support the app experience shown in `ux_existing`. They are written to guide later database schema, API, entitlement, and service design. Task-specific interaction behavior and prompt-generation/evaluation contracts are summarized in `design/tasks_trimmed.md`.

## Backend-Relevant Tech Stack

The following parts of the proposed stack are relevant to backend design:

- Python: backend language for APIs, services, repository implementations, and integration clients.
- Supabase + Postgres: primary backend, database, auth-adjacent storage, APIs, and server-side data model.
- RevenueCat: subscription purchase, entitlement, restore-purchase, and paywall-related state.
- PostHog: analytics, feature flag management, and session/video recording metadata where needed.
- Capgo: app update/release delivery service; relevant only where backend behavior depends on app version, channel, or rollout state.

The following stack items are primarily client/app concerns and are not expected to shape backend schema directly:

- Capacitor
- Ionic React
- Material UI / Paper component library

## Main Backend Requirements

### 1. User Identity And Profile

The backend shall support guest users, authenticated users, and user profile data.

Key backend needs:
- Create or track a guest user/session before login so onboarding and the first task can happen without authentication.
- Support Apple and Google authentication.
- Link guest progress to an authenticated account when the user signs in.
- Store profile fields needed by the app, including display name, current streak, and completed task count.
- Support sign-out/session invalidation.
- Use Supabase/Postgres as the system of record for user profile and progress data.

### 2. Onboarding State And Personalization

The backend shall track onboarding progress and the user's selected personalization trigger.

Key backend needs:
- Store the user's onboarding state and completed onboarding step.
- Store the selected trigger, such as group chats, dates, work, friends, stage, or being teased.
- Provide or assign the first tailored task based on the selected trigger.
- Record completion of the first task and mark onboarding milestones such as first win, account-save prompt, and reminder prompt.
- Allow onboarding to resume if the user leaves before finishing.

### 3. Task Catalog

The backend shall maintain a catalog of available tasks that can appear in onboarding, daily plans, and the Practice screen.

Key backend needs:
- Store task metadata: title, duration, type/category, thumbnail/icon, image, task text/content, availability, and ordering where needed.
- Ensure tasks of the same type can share the same client UI structure while varying their content and assets.
- Support the current voice task types defined in `design/tasks_trimmed.md`: `voice_single_prompt`, `voice_dialogue_prompt`, and `voice_scaffolded_prompt`.
- Keep product groupings such as sprint, improv, calm, and story as metadata/categories rather than conflating them with frontend/runtime task types.
- Support the current exercise catalog using the task type/runtime patterns in `design/tasks_trimmed.md`, including Yes And, Misinterpretation, Misinterpretation Techniques, Love/Hate, If by X you mean Y, Question Answer Tease, Vibing, Push/Pull, Heightening, and First Unusual Thing.
- Continue to support broader Practice-screen items shown in the mockups, including Warm-up riff, Box breathing, Peak-End hook, One-word story, Punch it up, 60-second story, and Power pose, as future catalog entries with their own task types where needed.
- Allow task definitions to be active, inactive, free, premium, or future-gated.
- Avoid hard-coding task-specific behavior into the general task catalog.
- Store client-renderable task copy/config in `tasks.content` and backend runtime pointers in `tasks.runtime_config`, following `design/tasks_trimmed.md`.

### 4. Daily Plan And Task Assignment

The backend shall generate or provide a user's daily task plan.

Key backend needs:
- Provide today's plan as an ordered list of task items.
- Identify exactly one next-up task for the user.
- Track each daily plan item status, such as completed, current, missed, or upcoming.
- Include enough task metadata for the client to render the plan without additional lookups where practical.
- Support plan continuity so users can pick up where they left off.

### 5. Task Progress, Attempts, And Streaks

The backend shall record user task activity and calculate progress indicators.

Key backend needs:
- Record task starts, completions, and the associated task type.
- Update completed task count after successful completion.
- Update daily progress and weekly activity status.
- Calculate and persist streak state.
- Preserve forgiving streak behavior where required, including cases where the free daily limit is reached.
- Keep progress personal; do not support leaderboard or public ranking requirements.

### 6. Subscription Entitlements And Free Limits

The backend shall support Witty+ entitlement state and daily free usage limits.

Key backend needs:
- Track whether a user has an active Witty+ entitlement.
- Enforce the mockup's free limit of three tasks per day for non-subscribed users.
- Return paywall eligibility/reason when the user reaches the free daily limit.
- Support annual and monthly plan identifiers from the subscription provider.
- Support restore-purchase and entitlement refresh flows.
- Expose entitlement-dependent access decisions, such as unlimited tasks, full library access, Role play availability, and no-ads status where applicable.
- Use RevenueCat as the subscription entitlement source.

### 7. Reminders And Notification Preferences

The backend shall store reminder preferences needed for daily warm-up nudges.

Key backend needs:
- Store selected reminder timing, such as before work, before going out, after dinner, or 8:00 PM.
- Store whether reminders are skipped or enabled.
- Store notification permission/device state where needed for delivery.
- Support updating or clearing reminder preferences.
- Ensure reminders are only scheduled after the user chooses a reminder option.

### 8. Support, Community, And App Configuration

The backend shall provide support-message handling and app-level configuration needed by the client.

Key backend needs:
- Accept support messages submitted from the "Chat with us" sheet.
- Store support message text, submitting user/session, timestamp, and delivery status.
- Route support messages to the intended human-read support channel.
- Provide configurable external links such as Telegram community, terms, and privacy.
- Provide feature/config flags for future or unavailable areas such as Role play.
- Use PostHog for feature flag management and product analytics where applicable.
- Account for Capgo release/update channels if a backend response must vary by app version or rollout group.

## Implied Backend Data Areas

- Users and auth identities
- Guest sessions
- User profiles
- Onboarding state
- Task definitions
- Daily plans and daily plan items
- Task attempts/completions
- Progress counters and streaks
- Usage counters and free-limit state
- Subscription entitlements
- Reminder preferences and notification devices
- Support messages
- App configuration and feature flags
- Product analytics events and feature flag evaluations
- App version, release channel, and rollout metadata where needed

## Out Of Scope For This Pass

- Exact AI prompt text, model selection, and prompt tuning.
- Exact database schema.
- Exact API route names and payloads.
- Exact subscription provider implementation details.

Detailed current task type behavior is in scope for `design/tasks_trimmed.md`; exact model prompt text and prompt tuning remain implementation details.
