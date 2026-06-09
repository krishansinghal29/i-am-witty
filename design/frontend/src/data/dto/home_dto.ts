/** Wire shapes for home / daily-plan endpoints (snake_case). */

export interface PlanItemDto {
  id: string;
  task_id: string;
  position: number;
  status: string;
  current_attempt_id: string | null;
}

export interface DailyPlanDto {
  id: string;
  plan_date: string;
  status: string;
  items: PlanItemDto[];
}

export interface ProgressDto {
  completed_task_count: number;
  current_streak_count: number;
  longest_streak_count: number;
  last_activity_date: string | null;
}

export interface HomeDto {
  plan: DailyPlanDto;
  progress: ProgressDto;
  access: { is_riffy_plus: boolean };
}
