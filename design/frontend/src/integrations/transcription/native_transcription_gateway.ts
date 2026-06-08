import { Capacitor } from '@capacitor/core';
import type { PluginListenerHandle } from '@capacitor/core';
import { SpeechRecognition } from '@capacitor-community/speech-recognition';

import type {
  TranscriptionGateway,
  TranscriptionResult,
  TranscriptionSession,
} from '@/integrations/ports/transcription_gateway';

/**
 * Offline/cheap fallback implementation of {@link TranscriptionGateway}.
 *
 * Uses the platform speech recognizer: the
 * `@capacitor-community/speech-recognition` plugin on native, and the
 * Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) on the
 * web. It never captures the answer audio, so `audioBase64` is always
 * `null`. As with the Deepgram gateway, every path fails soft: if no
 * recognizer is available or permission is denied, {@link
 * TranscriptionSession.stop} still resolves with whatever transcript was
 * captured (possibly an empty string).
 */
export class NativeTranscriptionGateway implements TranscriptionGateway {
  capabilities(): { streamingInterim: boolean } {
    return { streamingInterim: true };
  }

  async startSession(opts: {
    recordingLimitSeconds: number;
    language?: string;
  }): Promise<TranscriptionSession> {
    if (Capacitor.isNativePlatform()) {
      return this.startNativeSession(opts);
    }
    return this.startWebSession(opts);
  }

  private async startNativeSession(opts: {
    recordingLimitSeconds: number;
    language?: string;
  }): Promise<TranscriptionSession> {
    const { recordingLimitSeconds, language } = opts;
    const startedAt = Date.now();

    let latest = '';
    let interimCb: ((t: string) => void) | undefined;
    let settled = false;
    let listener: PluginListenerHandle | undefined;
    let limitTimer: ReturnType<typeof setTimeout> | undefined;

    const clearLimit = (): void => {
      if (limitTimer !== undefined) {
        clearTimeout(limitTimer);
        limitTimer = undefined;
      }
    };

    const cleanup = async (): Promise<void> => {
      clearLimit();
      try {
        await listener?.remove();
      } catch {
        // ignore
      }
      try {
        await SpeechRecognition.removeAllListeners();
      } catch {
        // ignore
      }
      try {
        await SpeechRecognition.stop();
      } catch {
        // ignore
      }
    };

    try {
      await SpeechRecognition.requestPermissions().catch(() => {});

      listener = await SpeechRecognition.addListener(
        'partialResults',
        (data: { matches: string[] }) => {
          const match = data.matches?.[0];
          if (typeof match === 'string') {
            latest = match;
            interimCb?.(match);
          }
        },
      );

      await SpeechRecognition.start({
        language: language ?? 'en-US',
        partialResults: true,
        popup: false,
      });

      const session: TranscriptionSession = {
        onInterim: (cb: (partialTranscript: string) => void): void => {
          interimCb = cb;
        },
        stop: async (): Promise<TranscriptionResult> => {
          settled = true;
          await cleanup();
          const transcript = latest.trim();
          return {
            transcript,
            audioBase64: null,
            contentType: null,
            durationSeconds: (Date.now() - startedAt) / 1000,
            metadata: {
              wordCount: transcript.split(/\s+/).filter(Boolean).length,
            },
          };
        },
        cancel: async (): Promise<void> => {
          settled = true;
          latest = '';
          await cleanup();
        },
      };

      limitTimer = setTimeout(() => {
        if (!settled) {
          void session.stop();
        }
      }, recordingLimitSeconds * 1000);

      return session;
    } catch {
      await cleanup();
      return noopSession(startedAt);
    }
  }

  private async startWebSession(opts: {
    recordingLimitSeconds: number;
    language?: string;
  }): Promise<TranscriptionSession> {
    const { recordingLimitSeconds, language } = opts;
    const startedAt = Date.now();

    // The Web Speech API has no DOM typings; treat it as `any`.
    const Ctor: any =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!Ctor) {
      return noopSession(startedAt);
    }

    let latest = '';
    let interimCb: ((t: string) => void) | undefined;
    let settled = false;
    let limitTimer: ReturnType<typeof setTimeout> | undefined;

    const clearLimit = (): void => {
      if (limitTimer !== undefined) {
        clearTimeout(limitTimer);
        limitTimer = undefined;
      }
    };

    try {
      const recognition: any = new Ctor();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = language ?? 'en-US';

      recognition.onresult = (event: any): void => {
        let assembled = '';
        for (let i = 0; i < event.results.length; i += 1) {
          const alt = event.results[i]?.[0];
          if (alt && typeof alt.transcript === 'string') {
            assembled += alt.transcript;
          }
        }
        latest = assembled;
        interimCb?.(assembled.trim());
      };

      recognition.start();

      const stopRecognition = (): void => {
        try {
          recognition.stop();
        } catch {
          // ignore
        }
      };

      const session: TranscriptionSession = {
        onInterim: (cb: (partialTranscript: string) => void): void => {
          interimCb = cb;
        },
        stop: async (): Promise<TranscriptionResult> => {
          settled = true;
          clearLimit();
          stopRecognition();
          const transcript = latest.trim();
          return {
            transcript,
            audioBase64: null,
            contentType: null,
            durationSeconds: (Date.now() - startedAt) / 1000,
            metadata: {
              wordCount: transcript.split(/\s+/).filter(Boolean).length,
            },
          };
        },
        cancel: async (): Promise<void> => {
          settled = true;
          latest = '';
          clearLimit();
          stopRecognition();
        },
      };

      limitTimer = setTimeout(() => {
        if (!settled) {
          void session.stop();
        }
      }, recordingLimitSeconds * 1000);

      return session;
    } catch {
      return noopSession(startedAt);
    }
  }
}

/** Fail-soft session that captures nothing and resolves an empty transcript. */
function noopSession(startedAt: number): TranscriptionSession {
  return {
    onInterim: (): void => {},
    stop: async (): Promise<TranscriptionResult> => ({
      transcript: '',
      audioBase64: null,
      contentType: null,
      durationSeconds: (Date.now() - startedAt) / 1000,
      metadata: { wordCount: 0 },
    }),
    cancel: async (): Promise<void> => {},
  };
}
