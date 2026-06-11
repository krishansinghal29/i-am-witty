import type {
  TranscriptionGateway,
  TranscriptionResult,
  TranscriptionSession,
  TranscriptionSessionStartOptions,
  TranscriptionWarmup,
  TranscriptionWarmupOptions,
} from '@/integrations/ports/transcription_gateway';
import type { TranscriptionToken } from '@/types/models';

/** Deepgram streaming model. nova-3 has a lower WER than nova-2. */
const DEEPGRAM_MODEL = 'nova-3';

/** How long to wait for Deepgram's trailing results after `CloseStream`. */
const FLUSH_TIMEOUT_MS = 1200;

/**
 * AudioWorklet that converts mic audio (Float32 at the context's native sample
 * rate) to 16-bit little-endian PCM and posts each render quantum to the main
 * thread. Loaded from a Blob URL so it needs no separately-bundled asset.
 */
const PCM_WORKLET_SRC = `
class PcmWorklet extends AudioWorkletProcessor {
  process(inputs) {
    const channel = inputs[0] && inputs[0][0];
    if (channel && channel.length) {
      const pcm = new Int16Array(channel.length);
      for (let i = 0; i < channel.length; i++) {
        let s = channel[i];
        s = s < -1 ? -1 : s > 1 ? 1 : s;
        pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
      }
      this.port.postMessage(pcm.buffer, [pcm.buffer]);
    }
    return true;
  }
}
registerProcessor('pcm-worklet', PcmWorklet);
`;

/**
 * Real Deepgram-backed implementation of {@link TranscriptionGateway}.
 *
 * Streams microphone audio to Deepgram over a raw browser `WebSocket` (no SDK)
 * using a short-lived ephemeral token minted backend-side. Audio is captured as
 * raw 16-bit PCM via the Web Audio API — never a `MediaRecorder` container — so
 * a single `linear16` path works identically across web, iOS (WKWebView) and
 * Android, with no codec/container fallback. The streamed transcript is
 * authoritative: the backend trusts it and never re-transcribes, so no answer
 * audio is retained or uploaded.
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
        await releaseConnection(connection);
        throw new Error('transcription_warmup_cancelled');
      }
      return connection;
    })();

    const cancel = async (): Promise<void> => {
      disposed = true;
      try {
        await releaseConnection(await ready);
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

    const entry = warmup ? this.warmupEntries.get(warmup) : undefined;
    const connection = entry
      ? await entry.take()
      : await openConnection(this.deps.mintToken, language ?? 'en-US');

    return buildSession({ connection, recordingLimitSeconds, onInterim });
  }
}

interface WarmedConnection {
  stream: MediaStream;
  ws: WebSocket;
  audioContext: AudioContext;
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
}

function buildSession(deps: BuildSessionDeps): TranscriptionSession {
  const { connection, recordingLimitSeconds, onInterim } = deps;
  const { stream, ws, audioContext } = connection;

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

  // Pipe mic PCM straight to the socket. The worklet's silent output keeps the
  // graph pulled when connected to the destination (no echo, since it writes no
  // samples).
  const source = audioContext.createMediaStreamSource(stream);
  const pcmNode = new AudioWorkletNode(audioContext, 'pcm-worklet');
  pcmNode.port.onmessage = (event: MessageEvent): void => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(event.data as ArrayBuffer);
    }
  };
  source.connect(pcmNode);
  pcmNode.connect(audioContext.destination);
  if (audioContext.state === 'suspended') {
    void audioContext.resume();
  }

  const stopCapture = (): void => {
    pcmNode.port.onmessage = null;
    try {
      source.disconnect();
    } catch {
      // ignore
    }
    try {
      pcmNode.disconnect();
    } catch {
      // ignore
    }
  };

  let limitTimer: ReturnType<typeof setTimeout> | undefined = setTimeout(() => {
    void session.stop();
  }, recordingLimitSeconds * 1000);

  const clearLimit = (): void => {
    if (limitTimer !== undefined) {
      clearTimeout(limitTimer);
      limitTimer = undefined;
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
        return { transcript: finalTranscript.trim(), durationSeconds: 0 };
      }
      settled = true;
      clearLimit();
      stopCapture();

      // Ask Deepgram to finalize, then wait briefly for the trailing results
      // (which still arrive on `ws.onmessage`) before closing the socket.
      try {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'CloseStream' }));
        }
      } catch {
        // ignore
      }
      await waitForClose(ws, FLUSH_TIMEOUT_MS);
      try {
        ws.close();
      } catch {
        // ignore
      }

      await closeAudio(audioContext);
      for (const track of stream.getTracks()) {
        try {
          track.stop();
        } catch {
          // ignore
        }
      }

      const transcript = finalTranscript.trim();
      return {
        transcript,
        durationSeconds: (Date.now() - startedAt) / 1000,
        metadata: { wordCount: countWords(transcript) },
      };
    },
    cancel: async (): Promise<void> => {
      settled = true;
      clearLimit();
      stopCapture();
      await releaseConnection(connection);
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

  const AudioCtx: typeof AudioContext =
    window.AudioContext ??
    (window as unknown as { webkitAudioContext: typeof AudioContext })
      .webkitAudioContext;
  const audioContext = new AudioCtx();

  try {
    await audioContext.audioWorklet.addModule(workletModuleUrl());

    // Deepgram must be told the exact PCM rate; we send the context's native
    // rate rather than resampling, which keeps the audio path lossless.
    const params = new URLSearchParams({
      model: DEEPGRAM_MODEL,
      smart_format: 'true',
      interim_results: 'true',
      encoding: 'linear16',
      sample_rate: String(Math.round(audioContext.sampleRate)),
      channels: '1',
      language,
    });
    const ws = new WebSocket(
      'wss://api.deepgram.com/v1/listen?' + params.toString(),
      deepgramWsProtocols(cred),
    );

    try {
      await waitForWsOpen(ws);
    } catch (err) {
      try {
        ws.close();
      } catch {
        // ignore
      }
      throw err;
    }

    return { stream, ws, audioContext };
  } catch (err) {
    await closeAudio(audioContext);
    for (const track of stream.getTracks()) {
      try {
        track.stop();
      } catch {
        // ignore
      }
    }
    throw err;
  }
}

async function releaseConnection(connection: WarmedConnection): Promise<void> {
  try {
    if (connection.ws.readyState === WebSocket.OPEN) {
      connection.ws.send(JSON.stringify({ type: 'CloseStream' }));
    }
    connection.ws.close();
  } catch {
    // ignore
  }
  await closeAudio(connection.audioContext);
  for (const track of connection.stream.getTracks()) {
    try {
      track.stop();
    } catch {
      // ignore
    }
  }
}

let cachedWorkletUrl: string | null = null;

/** Lazily build (and cache) the Blob URL for the PCM worklet module. */
function workletModuleUrl(): string {
  if (cachedWorkletUrl === null) {
    const blob = new Blob([PCM_WORKLET_SRC], { type: 'application/javascript' });
    cachedWorkletUrl = URL.createObjectURL(blob);
  }
  return cachedWorkletUrl;
}

async function closeAudio(ctx: AudioContext): Promise<void> {
  try {
    if (ctx.state !== 'closed') {
      await ctx.close();
    }
  } catch {
    // ignore
  }
}

/** Resolve when the socket closes, or after `timeoutMs` — whichever is first. */
function waitForClose(ws: WebSocket, timeoutMs: number): Promise<void> {
  if (ws.readyState === WebSocket.CLOSED) {
    return Promise.resolve();
  }
  return new Promise<void>((resolve) => {
    const done = (): void => {
      clearTimeout(timer);
      ws.removeEventListener('close', done);
      resolve();
    };
    const timer = setTimeout(done, timeoutMs);
    ws.addEventListener('close', done);
  });
}

function countWords(text: string): number {
  return text.split(/\s+/).filter(Boolean).length;
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
}

function extractTranscript(message: DeepgramMessage): string {
  return message.channel?.alternatives?.[0]?.transcript?.trim() ?? '';
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
