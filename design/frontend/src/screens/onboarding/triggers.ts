/**
 * The six onboarding trigger options. `value` mirrors the backend
 * `OnboardingTrigger` enum exactly (group_chats | dates | work | friends |
 * stage | teased); the rest is presentation copy for the trigger + tiny-practice
 * steps.
 */

export type TriggerValue =
  | 'group_chats'
  | 'dates'
  | 'work'
  | 'friends'
  | 'stage'
  | 'teased';

export interface TriggerOption {
  value: TriggerValue;
  label: string;
  emoji: string;
  /** "Tuned for …" phrase shown on the tiny-practice step. */
  forPhrase: string;
}

export const TRIGGER_OPTIONS: readonly TriggerOption[] = [
  { value: 'group_chats', label: 'Group chats', emoji: '💬', forPhrase: 'group chats' },
  { value: 'dates', label: 'Dates', emoji: '💘', forPhrase: 'dates' },
  { value: 'work', label: 'Work', emoji: '💼', forPhrase: 'work' },
  { value: 'friends', label: 'With friends', emoji: '👥', forPhrase: 'time with friends' },
  { value: 'stage', label: 'On stage', emoji: '🎤', forPhrase: 'the stage' },
  { value: 'teased', label: 'When someone teases me', emoji: '😏', forPhrase: 'quick comebacks' },
] as const;

/** Look up a trigger option by its backend value. */
export function triggerByValue(value: string | null | undefined): TriggerOption | null {
  if (!value) return null;
  return TRIGGER_OPTIONS.find((option) => option.value === value) ?? null;
}
