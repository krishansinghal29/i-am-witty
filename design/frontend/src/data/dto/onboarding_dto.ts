/** Wire shapes for onboarding endpoints (snake_case). */

export interface OnboardingStateDto {
  current_step: string;
  selected_trigger: string | null;
  first_task_id: string | null;
  first_task_attempt_id: string | null;
  completed_at: string | null;
}
