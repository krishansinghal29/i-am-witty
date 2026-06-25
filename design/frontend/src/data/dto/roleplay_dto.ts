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
  sample_answer: string;
  /** Multi-phase roleplays only: the move the user should make on their NEXT
   *  turn (e.g. "ask"/"tease", "love"/"hate"). Null for single-phase roleplays. */
  next_user_move?: string | null;
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
