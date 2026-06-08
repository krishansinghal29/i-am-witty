/** Maps transcription DTOs → TranscriptionToken view-model. */

import { TranscriptionToken } from '@/types/models';
import { TranscriptionTokenDto } from '@/data/dto/transcription_dto';

export function mapTranscriptionToken(dto: TranscriptionTokenDto): TranscriptionToken {
  return {
    token: dto.token,
    expiresAt: dto.expires_at,
    provider: dto.provider,
    extra: dto.extra,
  };
}
