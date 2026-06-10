export interface TranscriptionMetadata {
  wordCount?: number;
  pauseCount?: number; // needs word-level timings; not all providers expose this
}

export interface TranscriptionResult {
  transcript: string;
  audioBase64: string | null; // the USER's answer audio (optional upload for backend confirmation)
  contentType: string | null;
  durationSeconds: number;
  metadata?: TranscriptionMetadata;
}

export interface TranscriptionSession {
  onInterim?(cb: (partialTranscript: string) => void): void; // streaming providers emit; batch ones don't
  stop(): Promise<TranscriptionResult>;
  cancel(): Promise<void>;
}

export interface TranscriptionSessionStartOptions {
  recordingLimitSeconds: number;
  language?: string;
  /** Register before audio/transcripts flow to avoid missing early interim frames. */
  onInterim?: (partialTranscript: string) => void;
}

export interface TranscriptionGateway {
  startSession(opts: TranscriptionSessionStartOptions): Promise<TranscriptionSession>;
  capabilities(): { streamingInterim: boolean };
}
