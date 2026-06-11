export interface TranscriptionMetadata {
  wordCount?: number;
  pauseCount?: number; // needs word-level timings; not all providers expose this
}

export interface TranscriptionResult {
  transcript: string;
  durationSeconds: number;
  metadata?: TranscriptionMetadata;
}

export interface TranscriptionSession {
  onInterim?(cb: (partialTranscript: string) => void): void; // streaming providers emit; batch ones don't
  stop(): Promise<TranscriptionResult>;
  cancel(): Promise<void>;
}

export interface TranscriptionWarmupOptions {
  language?: string;
}

/** Pre-opened mic + provider connection; consumed by {@link TranscriptionGateway.startSession}. */
export interface TranscriptionWarmup {
  /** Resolves when warmed resources are ready (or rejects on setup failure). */
  readonly ready: Promise<void>;
  /** Release warmed resources without starting a capture session. */
  cancel(): Promise<void>;
}

export interface TranscriptionSessionStartOptions {
  recordingLimitSeconds: number;
  language?: string;
  /** When provided, reuses resources from an earlier {@link TranscriptionGateway.warmup}. */
  warmup?: TranscriptionWarmup;
  /** Register before audio/transcripts flow to avoid missing early interim frames. */
  onInterim?: (partialTranscript: string) => void;
}

export interface TranscriptionGateway {
  /** Best-effort pre-connect before the user taps speak (token, mic, socket). */
  warmup(opts?: TranscriptionWarmupOptions): TranscriptionWarmup;
  startSession(opts: TranscriptionSessionStartOptions): Promise<TranscriptionSession>;
  capabilities(): { streamingInterim: boolean };
}
