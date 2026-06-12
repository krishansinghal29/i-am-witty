/**
 * The six onboarding trigger options. `value` mirrors the backend
 * `OnboardingTrigger` enum (group_chats | dates | work | friends | stage |
 * other). The legacy `teased` value is retained server-side for older clients
 * but is no longer offered here. The rest is presentation copy for the step.
 */

export type TriggerValue =
  | 'group_chats'
  | 'dates'
  | 'work'
  | 'friends'
  | 'stage'
  | 'other';

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
  { value: 'other', label: 'Something else', emoji: '✨' },
] as const;

/** Look up a trigger option by its backend value. */
export function triggerByValue(value: string | null | undefined): TriggerOption | null {
  if (!value) return null;
  return TRIGGER_OPTIONS.find((option) => option.value === value) ?? null;
}
