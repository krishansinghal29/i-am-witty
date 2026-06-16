/** Wire shapes for task attempt (start / complete) endpoints (snake_case). */

export interface FreeLimitDto {
  allowed: boolean;
  should_paywall: boolean;
  remaining: number;
  reason: string | null;
}

export interface StartTaskDto {
  attempt_id: string;
  task_id: string;
  status: string;
  free_limit: FreeLimitDto;
}

export interface EvaluationDto {
  style_label: string | null;
  feedback_html: string;
  sample_answer_html: string;
  completion_metadata: Record<string, unknown>;
}

export interface StreakDto {
  current_streak: number;
  longest_streak: number;
  last_qualified_date: string;
}

export interface CompleteTaskDto {
  attempt_id: string;
  status: string;
  result: EvaluationDto;
  free_limit: FreeLimitDto;
  streak: StreakDto;
}

// ---------------------------------------------------------------------------
// Request bodies
// ---------------------------------------------------------------------------

export interface CompleteTaskRequestDto {
  client_transcript?: string | null;
  audio_base64?: string | null;
  content_type?: string | null;
  language?: string | null;
}
