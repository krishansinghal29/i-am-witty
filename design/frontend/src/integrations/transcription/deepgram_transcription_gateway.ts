import type {
  TranscriptionGateway,
  TranscriptionResult,
  TranscriptionSession,
  TranscriptionSessionStartOptions,
  TranscriptionWarmup,
  TranscriptionWarmupOptions,
} from '@/integrations/ports/transcription_gateway';
import type { TranscriptionToken } from '@/types/models';

/** MediaRecorder timeslice — smaller first chunk for faster live STT. */
const CHUNK_TIMESLICE_MS = 100;
/** Nudge interval for browsers that buffer MediaRecorder output until stop. */
const CHUNK_PUMP_MS = 100;

/**
 * Real Deepgram-backed implementation of {@link TranscriptionGateway}.
 *
 * Streams microphone audio to Deepgram over a raw browser `WebSocket`
 * (no SDK) using a short-lived ephemeral token minted backend-side. The
 * live interim transcript is best-effort and cosmetic; the authoritative
 * final transcript is produced backend-side from the uploaded answer audio.
 *
 * The composition root injects {@link mintToken}, which calls the backend
 * `POST /v1/transcription-tokens`; the API client is intentionally not
 * imported here.
 */
export class DeepgramTranscriptionGateway implements TranscriptionGateway {
  private readonly warmupEntries = new WeakMap<TranscriptionWarmup, WarmupEntry>();

  constructor(private deps: { mintToken: () => Promise<TranscriptionToken> }) {}

  capabilities(): { streamingInterim: boolean } {
    return { streamingInterim: true };
  }

  warmup(opts?: TranscriptionWarmupOptions): TranscriptionWarmup {
    const language = opts?.language ?? 'en-US';
    let disposed = false;

    const ready = (async (): Promise<WarmedConnection> => {
      const connection = await openConnection(this.deps.mintToken, language);
      if (disposed) {
        releaseConnection(connection);
        throw new Error('transcription_warmup_cancelled');
      }
      return connection;
    })();

    const cancel = async (): Promise<void> => {
      disposed = true;
      try {
        const connection = await ready;
        releaseConnection(connection);
      } catch {
        // Setup failed or was already torn down.
      }
    };

    const handle: TranscriptionWarmup = {
      ready: ready.then(
        () => {},
        () => {},
      ),
      cancel,
    };

    this.warmupEntries.set(handle, {
      ready,
      take: async (): Promise<WarmedConnection> => {
        disposed = true;
        this.warmupEntries.delete(handle);
        return ready;
      },
      cancel,
    });

    return handle;
  }

  async startSession(
    opts: TranscriptionSessionStartOptions,
  ): Promise<TranscriptionSession> {
    const { recordingLimitSeconds, language, onInterim, warmup } = opts;

    try {
      const entry = warmup ? this.warmupEntries.get(warmup) : undefined;
      const connection = entry
        ? await entry.take()
        : await openConnection(this.deps.mintToken, language ?? 'en-US');

      return buildSession({
        connection,
        recordingLimitSeconds,
        onInterim,
        blobToBase64: (blob) => this.blobToBase64(blob),
      });
    } catch (err) {
      throw err;
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
        const comma = result.indexOf(',');
        resolve(comma >= 0 ? result.slice(comma + 1) : result);
      };
      reader.onerror = (): void => reject(reader.error ?? new Error('read error'));
      reader.readAsDataURL(blob);
    });
  }
}

interface WarmedConnection {
  stream: MediaStream;
  ws: WebSocket;
}

interface WarmupEntry {
  ready: Promise<WarmedConnection>;
  take: () => Promise<WarmedConnection>;
  cancel: () => Promise<void>;
}

interface BuildSessionDeps {
  connection: WarmedConnection;
  recordingLimitSeconds: number;
  onInterim?: (partialTranscript: string) => void;
  blobToBase64: (blob: Blob) => Promise<string>;
}

function buildSession(deps: BuildSessionDeps): TranscriptionSession {
  const { connection, recordingLimitSeconds, onInterim, blobToBase64 } = deps;
  const { stream, ws } = connection;

  const chunks: Blob[] = [];
  const { recorder, contentType } = createAudioRecorder(stream);

  let finalTranscript = '';
  let interimCb: ((t: string) => void) | undefined = onInterim;
  let pendingInterim: string | null = null;
  let settled = false;

  const startedAt = Date.now();

  const emitInterim = (text: string): void => {
    if (interimCb) {
      interimCb(text);
    } else {
      pendingInterim = text;
    }
  };

  const sendChunk = (chunk: Blob): void => {
    if (!chunk.size || ws.readyState !== WebSocket.OPEN) return;
    chunks.push(chunk);
    ws.send(chunk);
  };

  recorder.addEventListener('dataavailable', (event: BlobEvent) => {
    if (event.data?.size) {
      sendChunk(event.data);
    }
  });

  const handleWsMessage = async (payload: unknown): Promise<void> => {
    try {
      const data = parseDeepgramMessage(await readWsPayload(payload));
      if (data.error) {
        return;
      }
      const segment = extractTranscript(data);
      if (!segment) {
        return;
      }
      if (data.is_final) {
        finalTranscript = (finalTranscript + ' ' + segment).trim();
        emitInterim(finalTranscript);
      } else {
        emitInterim((finalTranscript + ' ' + segment).trim());
      }
    } catch {
      // Ignore malformed frames; interim transcript is best-effort.
    }
  };

  ws.onmessage = (event: MessageEvent) => {
    void handleWsMessage(event.data);
  };

  recorder.start(CHUNK_TIMESLICE_MS);
  queueFirstChunk(recorder);

  const pumpTimer = setInterval(() => {
    if (recorder.state !== 'recording') return;
    try {
      recorder.requestData();
    } catch {
      // requestData is not available on every platform.
    }
  }, CHUNK_PUMP_MS);

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

  const clearPump = (): void => {
    clearInterval(pumpTimer);
  };

  const teardown = (): void => {
    clearLimit();
    clearPump();
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
      if (pendingInterim !== null) {
        cb(pendingInterim);
        pendingInterim = null;
      }
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
      clearPump();

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
          audioBase64 = await blobToBase64(new Blob(chunks, { type: contentType }));
        }
      } catch {
        audioBase64 = null;
      }

      const transcript = finalTranscript.trim();
      const wordCount = transcript.split(/\s+/).filter(Boolean).length;

      return {
        transcript,
        audioBase64,
        contentType,
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
}

async function openConnection(
  mintToken: () => Promise<TranscriptionToken>,
  language: string,
): Promise<WarmedConnection> {
  const cred = await mintToken();
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  const ws = new WebSocket(
    'wss://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&interim_results=true&language=' +
      encodeURIComponent(language),
    deepgramWsProtocols(cred),
  );

  await waitForWsOpen(ws);
  return { stream, ws };
}

function releaseConnection(connection: WarmedConnection): void {
  try {
    if (connection.ws.readyState === WebSocket.OPEN) {
      connection.ws.send(JSON.stringify({ type: 'CloseStream' }));
    }
    connection.ws.close();
  } catch {
    // ignore
  }
  for (const track of connection.stream.getTracks()) {
    try {
      track.stop();
    } catch {
      // ignore
    }
  }
}

function queueFirstChunk(recorder: MediaRecorder): void {
  queueMicrotask(() => {
    if (recorder.state !== 'recording') return;
    try {
      recorder.requestData();
    } catch {
      // requestData is not available on every platform.
    }
  });
}

function delay(ms: number): Promise<void> {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}

interface DeepgramMessage {
  type?: string;
  is_final?: boolean;
  error?: string;
  channel?: {
    alternatives?: {
      transcript?: string;
    }[];
  };
  results?: {
    channels?: {
      alternatives?: {
        transcript?: string;
      }[];
    }[];
  };
}

function extractTranscript(message: DeepgramMessage): string {
  const live = message.channel?.alternatives?.[0]?.transcript;
  if (live?.trim()) return live;
  return message.results?.channels?.[0]?.alternatives?.[0]?.transcript?.trim() ?? '';
}

function isBearerToken(cred: TranscriptionToken): boolean {
  const scheme = cred.extra?.auth_scheme;
  if (typeof scheme === 'string' && scheme.toLowerCase() === 'bearer') {
    return true;
  }
  return cred.token.startsWith('eyJ');
}

/** Matches @deepgram/sdk browser auth: ["bearer", jwt] or ["token", apiKey]. */
function deepgramWsProtocols(cred: TranscriptionToken): string[] {
  return isBearerToken(cred) ? ['bearer', cred.token] : ['token', cred.token];
}

function waitForWsOpen(ws: WebSocket, timeoutMs = 10_000): Promise<void> {
  if (ws.readyState === WebSocket.OPEN) {
    return Promise.resolve();
  }

  return new Promise<void>((resolve, reject) => {
    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error('deepgram_ws_timeout'));
    }, timeoutMs);

    const onOpen = (): void => {
      cleanup();
      resolve();
    };

    const onError = (): void => {
      cleanup();
      reject(new Error('deepgram_ws_error'));
    };

    const onClose = (): void => {
      if (ws.readyState !== WebSocket.OPEN) {
        cleanup();
        reject(new Error('deepgram_ws_closed'));
      }
    };

    const cleanup = (): void => {
      clearTimeout(timeout);
      ws.removeEventListener('open', onOpen);
      ws.removeEventListener('error', onError);
      ws.removeEventListener('close', onClose);
    };

    ws.addEventListener('open', onOpen);
    ws.addEventListener('error', onError);
    ws.addEventListener('close', onClose);
  });
}

function createAudioRecorder(stream: MediaStream): {
  recorder: MediaRecorder;
  contentType: string;
} {
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/ogg;codecs=opus',
  ];
  for (const mimeType of candidates) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(mimeType)) {
      try {
        return { recorder: new MediaRecorder(stream, { mimeType }), contentType: mimeType };
      } catch {
        // isTypeSupported can lie on some mobile browsers; try the next candidate.
      }
    }
  }
  return { recorder: new MediaRecorder(stream), contentType: 'audio/webm' };
}

async function readWsPayload(data: unknown): Promise<string> {
  if (typeof data === 'string') return data;
  if (data instanceof Blob) return data.text();
  if (data instanceof ArrayBuffer) return new TextDecoder().decode(data);
  return '';
}

function parseDeepgramMessage(raw: string): DeepgramMessage {
  if (!raw) return {};
  const parsed: unknown = JSON.parse(raw);
  if (!parsed || typeof parsed !== 'object') return {};
  const message = parsed as DeepgramMessage;
  const type = message.type?.toLowerCase();
  if (type === 'metadata' || type === 'error') {
    return { error: message.type };
  }
  if (type && type !== 'results') return {};
  return message;
}
