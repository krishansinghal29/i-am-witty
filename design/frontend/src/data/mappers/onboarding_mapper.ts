/** Maps onboarding DTOs → OnboardingState view-model. */

import { OnboardingState } from '@/types/models';
import { OnboardingStateDto } from '@/data/dto/onboarding_dto';

export function mapOnboardingState(dto: OnboardingStateDto): OnboardingState {
  return {
    currentStep: dto.current_step,
    selectedTrigger: dto.selected_trigger,
    firstTaskId: dto.first_task_id,
    firstTaskAttemptId: dto.first_task_attempt_id,
    completedAt: dto.completed_at,
  };
}
