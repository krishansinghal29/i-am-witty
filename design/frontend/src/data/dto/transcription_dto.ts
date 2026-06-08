/** Wire shapes for transcription token endpoints (snake_case). */

export interface TranscriptionTokenDto {
  token: string;
  expires_at: string | null;
  provider: string;
  extra: Record<string, unknown>;
}
