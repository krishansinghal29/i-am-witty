/** Maps roleplay turn DTOs → view-models. */

import { RolePlayTurn, TurnTaskResult } from '@/types/models';
import { RolePlayTurnDto, TurnTaskDto } from '@/data/dto/roleplay_dto';
import { mapFreeLimit, mapStreak } from './attempt_mapper';

export function mapRolePlayTurn(dto: RolePlayTurnDto): RolePlayTurn {
  return {
    narration: dto.narration,
    dialogue: dto.dialogue,
    landed: dto.landed,
    intensity: dto.intensity,
    landedCount: dto.landed_count,
    targetCount: dto.target_count,
    isComplete: dto.is_complete,
    sampleAnswer: dto.sample_answer,
    nextUserMove: dto.next_user_move ?? null,
    audio: {
      audioBase64: dto.audio_base64,
      contentType: dto.audio_content_type,
    },
  };
}

export function mapTurnResult(dto: TurnTaskDto): TurnTaskResult {
  return {
    attemptId: dto.attempt_id,
    status: dto.status,
    turn: mapRolePlayTurn(dto.turn),
    freeLimit: mapFreeLimit(dto.free_limit),
    streak: dto.streak != null ? mapStreak(dto.streak) : null,
  };
}
