/** Maps attempt DTOs → StartTaskResult / CompleteTaskResult view-models. */

import {
  CompleteTaskResult,
  EvaluationResult,
  FreeLimit,
  NextRoundResult,
  StartTaskResult,
  Streak,
} from '@/types/models';
import {
  CompleteTaskDto,
  EvaluationDto,
  FreeLimitDto,
  NextRoundDto,
  StartTaskDto,
  StreakDto,
} from '@/data/dto/attempt_dto';
import { mapPayload, mapRounds } from './task_runtime_mapper';

export function mapFreeLimit(dto: FreeLimitDto): FreeLimit {
  return {
    allowed: dto.allowed,
    shouldPaywall: dto.should_paywall,
    remaining: dto.remaining,
    reason: dto.reason,
  };
}

export function mapEvaluation(dto: EvaluationDto): EvaluationResult {
  return {
    styleLabel: dto.style_label,
    feedbackHtml: dto.feedback_html,
    sampleAnswerHtml: dto.sample_answer_html,
    completionMetadata: dto.completion_metadata,
  };
}

export function mapStreak(dto: StreakDto): Streak {
  return {
    currentStreak: dto.current_streak,
    longestStreak: dto.longest_streak,
    lastQualifiedDate: dto.last_qualified_date,
  };
}

export function mapStartResult(dto: StartTaskDto): StartTaskResult {
  return {
    attemptId: dto.attempt_id,
    taskId: dto.task_id,
    status: dto.status,
    freeLimit: mapFreeLimit(dto.free_limit),
  };
}

export function mapCompleteResult(dto: CompleteTaskDto): CompleteTaskResult {
  return {
    attemptId: dto.attempt_id,
    status: dto.status,
    result: mapEvaluation(dto.result),
    freeLimit: mapFreeLimit(dto.free_limit),
    rounds: mapRounds(dto.rounds),
    isSessionComplete: dto.is_session_complete,
    streak: dto.streak != null ? mapStreak(dto.streak) : null,
  };
}

export function mapNextRoundResult(dto: NextRoundDto): NextRoundResult {
  return {
    attemptId: dto.attempt_id,
    status: dto.status,
    payload: mapPayload(dto.payload),
    rounds: mapRounds(dto.rounds),
    freeLimit: mapFreeLimit(dto.free_limit),
  };
}
