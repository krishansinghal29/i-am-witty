/**
 * Onboarding machine — pure mapping/transition logic.
 *
 * The backend's `OnboardingStep` enum (see
 * `backend/app/infrastructure/db/orm/onboarding.py`) is the source of truth for
 * the early steps it actually drives (`trigger_question` -> `first_task`, and
 * `first_task` -> `first_win` once the first attempt is completed). The six UX
 * steps are mapped from it here. Everything is a pure function over the open
 * `string` union so an unknown future backend value degrades to the first step
 * rather than throwing.
 */

import type { OnboardingState } from '@/types/models';

/** The six onboarding UX steps, in order. */
export type UxStep =
  | 'trigger'
  | 'tiny_practice'
  | 'variable_reward'
  | 'login'
  | 'reminder'
  | 'plan_landing';

export const UX_STEPS: readonly UxStep[] = [
  'trigger',
  'tiny_practice',
  'variable_reward',
  'login',
  'reminder',
  'plan_landing',
] as const;

/** Authoritative backend `OnboardingStep` values (raw, snake_case). */
export const BACKEND_STEPS = {
  triggerQuestion: 'trigger_question',
  firstTask: 'first_task',
  firstWin: 'first_win',
  accountPrompt: 'account_prompt',
  reminderPrompt: 'reminder_prompt',
  complete: 'complete',
} as const;

const BACKEND_TO_UX: Record<string, UxStep> = {
  trigger_question: 'trigger',
  first_task: 'tiny_practice',
  first_win: 'variable_reward',
  account_prompt: 'login',
  reminder_prompt: 'reminder',
  complete: 'plan_landing',
};

/** Index of a UX step within {@link UX_STEPS} (0-based). */
export function uxStepIndex(step: UxStep): number {
  return UX_STEPS.indexOf(step);
}

/** Map a raw backend step value to its UX step (tolerant of unknown values). */
export function backendStepToUxStep(step: string): UxStep {
  return BACKEND_TO_UX[step] ?? 'trigger';
}

/** Resolve the UX step implied by a full backend onboarding state. */
export function uxStepForState(state: OnboardingState | null): UxStep {
  if (!state) return 'trigger';
  if (state.completedAt) return 'plan_landing';
  return backendStepToUxStep(state.currentStep);
}

/** The UX step after `step` (clamped at the final step). */
export function nextUxStep(step: UxStep): UxStep {
  const i = uxStepIndex(step);
  return UX_STEPS[Math.min(i + 1, UX_STEPS.length - 1)];
}

/** The UX step before `step` (clamped at the first step). */
export function prevUxStep(step: UxStep): UxStep {
  const i = uxStepIndex(step);
  return UX_STEPS[Math.max(i - 1, 0)];
}

/**
 * True once the user has produced their "first win". The backend marks this by
 * advancing to `first_win` (or by stamping `first_task_attempt_id`); callers may
 * also pass a progress-derived signal for resilience when the backend step has
 * not advanced yet.
 */
export function hasFirstWin(state: OnboardingState | null): boolean {
  if (!state) return false;
  if (state.firstTaskAttemptId) return true;
  return (
    uxStepIndex(backendStepToUxStep(state.currentStep)) >=
    uxStepIndex('variable_reward')
  );
}

/** Number of segments shown in the onboarding progress bar. */
export const PROGRESS_SEGMENTS = 5;

/** How many progress segments are filled at a given step. */
export function progressFilled(step: UxStep): number {
  return Math.min(uxStepIndex(step) + 1, PROGRESS_SEGMENTS);
}
