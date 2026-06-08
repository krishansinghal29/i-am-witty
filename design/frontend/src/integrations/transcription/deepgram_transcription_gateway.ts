import type {
  TranscriptionGateway,
  TranscriptionResult,
  TranscriptionSession,
} from '@/integrations/ports/transcription_gateway';
import type { TranscriptionToken } from '@/types/models';

/**
 * Real Deepgram-backed implementation of {@link TranscriptionGateway}.
 *
 * Streams microphone audio to Deepgram over a raw browser `WebSocket`
 * (no SDK) using a short-lived ephemeral token minted backend-side. The
 * live interim transcript is best-effort and cosmetic; the authoritative
 * final transcript is produced backend-side from the uploaded answer audio.
 * Every code path therefore fails soft: if the mic, permission or socket
 * setup fails, {@link TranscriptionSession.stop} still resolves (with an
 * empty transcript) rather than throwing.
 *
 * The composition root injects {@link mintToken}, which calls the backend
 * `POST /v1/transcription-tokens`; the API client is intentionally not
 * imported here.
 */
export class DeepgramTranscriptionGateway implements TranscriptionGateway {
  constructor(private deps: { mintToken: () => Promise<TranscriptionToken> }) {}

  capabilities(): { streamingInterim: boolean } {
    return { streamingInterim: true };
  }

  async startSession(opts: {
    recordingLimitSeconds: number;
    language?: string;
  }): Promise<TranscriptionSession> {
    const { recordingLimitSeconds, language } = opts;

    try {
      const cred = await this.deps.mintToken();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const ws = new WebSocket(
        'wss://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&interim_results=true&language=' +
          (language ?? 'en'),
        ['token', cred.token],
      );

      const chunks: Blob[] = [];
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      let finalTranscript = '';
      let interimCb: ((t: string) => void) | undefined;
      let settled = false;

      const startedAt = Date.now();

      recorder.addEventListener('dataavailable', (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          chunks.push(event.data);
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(event.data);
          }
        }
      });

      ws.onmessage = (event: MessageEvent) => {
        try {
          // Deepgram JSON: { channel: { alternatives: [{ transcript }] }, is_final }
          const data = JSON.parse(event.data as string) as any;
          const transcript: string =
            data?.channel?.alternatives?.[0]?.transcript ?? '';
          if (!transcript) {
            return;
          }
          if (data.is_final) {
            finalTranscript = (finalTranscript + ' ' + transcript).trim();
          } else {
            interimCb?.((finalTranscript + ' ' + transcript).trim());
          }
        } catch {
          // Ignore malformed frames; interim transcript is best-effort.
        }
      };

      recorder.start(250);

      let limitTimer: ReturnType<typeof setTimeout> | undefined = setTimeout(
        () => {
          void session.stop();
        },
        recordingLimitSeconds * 1000,
      );

      const clearLimit = (): void => {
        if (limitTimer !== undefined) {
          clearTimeout(limitTimer);
          limitTimer = undefined;
        }
      };

      const teardown = (): void => {
        clearLimit();
        try {
          if (recorder.state !== 'inactive') {
            recorder.stop();
          }
        } catch {
          // ignore
        }
        try {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'CloseStream' }));
          }
          ws.close();
        } catch {
          // ignore
        }
        for (const track of stream.getTracks()) {
          try {
            track.stop();
          } catch {
            // ignore
          }
        }
      };

      const session: TranscriptionSession = {
        onInterim: (cb: (partialTranscript: string) => void): void => {
          interimCb = cb;
        },
        stop: async (): Promise<TranscriptionResult> => {
          if (settled) {
            return {
              transcript: finalTranscript.trim(),
              audioBase64: null,
              contentType: null,
              durationSeconds: 0,
            };
          }
          settled = true;
          clearLimit();

          // Let the final dataavailable fire and the socket flush.
          try {
            if (recorder.state !== 'inactive') {
              recorder.stop();
            }
          } catch {
            // ignore
          }
          await delay(300);

          try {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: 'CloseStream' }));
            }
            ws.close();
          } catch {
            // ignore
          }

          for (const track of stream.getTracks()) {
            try {
              track.stop();
            } catch {
              // ignore
            }
          }

          let audioBase64: string | null = null;
          try {
            if (chunks.length > 0) {
              audioBase64 = await this.blobToBase64(
                new Blob(chunks, { type: 'audio/webm' }),
              );
            }
          } catch {
            audioBase64 = null;
          }

          const transcript = finalTranscript.trim();
          const wordCount = transcript.split(/\s+/).filter(Boolean).length;

          return {
            transcript,
            audioBase64,
            contentType: 'audio/webm',
            durationSeconds: (Date.now() - startedAt) / 1000,
            metadata: { wordCount },
          };
        },
        cancel: async (): Promise<void> => {
          settled = true;
          chunks.length = 0;
          teardown();
        },
      };

      return session;
    } catch {
      // Fail soft: mic/permission/WebSocket setup failed.
      return {
        onInterim: (): void => {},
        stop: async (): Promise<TranscriptionResult> => ({
          transcript: '',
          audioBase64: null,
          contentType: null,
          durationSeconds: 0,
        }),
        cancel: async (): Promise<void> => {},
      };
    }
  }

  private blobToBase64(blob: Blob): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = (): void => {
        const result = reader.result;
        if (typeof result !== 'string') {
          reject(new Error('Unexpected FileReader result'));
          return;
        }
        // Strip the `data:<mime>;base64,` prefix.
        const comma = result.indexOf(',');
        resolve(comma >= 0 ? result.slice(comma + 1) : result);
      };
      reader.onerror = (): void => reject(reader.error ?? new Error('read error'));
      reader.readAsDataURL(blob);
    });
  }
}

function delay(ms: number): Promise<void> {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
