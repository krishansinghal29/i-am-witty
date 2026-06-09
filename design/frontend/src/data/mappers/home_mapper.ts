/** Maps home / daily-plan DTOs → view-models. */

import { DailyPlan, HomeView, PlanItem, Progress } from '@/types/models';
import { DailyPlanDto, HomeDto, PlanItemDto, ProgressDto } from '@/data/dto/home_dto';

export function mapPlanItem(dto: PlanItemDto): PlanItem {
  return {
    id: dto.id,
    taskId: dto.task_id,
    position: dto.position,
    status: dto.status,
    currentAttemptId: dto.current_attempt_id,
  };
}

export function mapDailyPlan(dto: DailyPlanDto): DailyPlan {
  return {
    id: dto.id,
    planDate: dto.plan_date,
    status: dto.status,
    items: dto.items.map(mapPlanItem),
  };
}

export function mapProgress(dto: ProgressDto): Progress {
  return {
    completedTaskCount: dto.completed_task_count,
    currentStreakCount: dto.current_streak_count,
    longestStreakCount: dto.longest_streak_count,
    lastActivityDate: dto.last_activity_date,
  };
}

export function mapHome(dto: HomeDto): HomeView {
  return {
    plan: mapDailyPlan(dto.plan),
    progress: mapProgress(dto.progress),
    access: { isRiffyPlus: dto.access.is_riffy_plus },
  };
}
