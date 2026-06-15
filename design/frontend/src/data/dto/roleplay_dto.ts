/** Wire shapes for the roleplay turn endpoint (snake_case). */

import { FreeLimitDto, StreakDto } from './attempt_dto';

export interface TurnRequestDto {
  client_transcript?: string;
}

export interface RolePlayTurnDto {
  narration: string;
  dialogue: string;
  landed: boolean;
  intensity: string;
  landed_count: number;
  target_count: number;
  is_complete: boolean;
  audio_base64: string | null;
  audio_content_type: string | null;
}

export interface TurnTaskDto {
  attempt_id: string;
  status: string;
  turn: RolePlayTurnDto;
  free_limit: FreeLimitDto;
  streak: StreakDto | null;
}
