/**
 * The six onboarding trigger options. `value` mirrors the backend
 * `OnboardingTrigger` enum exactly (group_chats | dates | work | friends |
 * stage | teased); the rest is presentation copy for the trigger step.
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
}

export const TRIGGER_OPTIONS: readonly TriggerOption[] = [
  { value: 'group_chats', label: 'Group chats', emoji: '💬' },
  { value: 'dates', label: 'Dates', emoji: '💘' },
  { value: 'work', label: 'Work', emoji: '💼' },
  { value: 'friends', label: 'With friends', emoji: '👥' },
  { value: 'stage', label: 'On stage', emoji: '🎤' },
  { value: 'teased', label: 'When someone teases me', emoji: '😏' },
] as const;

/** Look up a trigger option by its backend value. */
export function triggerByValue(value: string | null | undefined): TriggerOption | null {
  if (!value) return null;
  return TRIGGER_OPTIONS.find((option) => option.value === value) ?? null;
}
