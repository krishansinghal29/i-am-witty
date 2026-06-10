/**
 * Minimal typed HTTP client used by RiffyApi.
 *
 * Auth strategy: a Firebase id-token → `Authorization: Bearer <token>`, or no
 * header when signed out. (There are no guests; every user is authenticated.)
 *
 * All non-2xx responses are normalised to AppError via AppError.fromHttp().
 * Network/throw errors are normalised via AppError.from().
 */

import { AppError } from '@/data/errors/app_error';

// ---------------------------------------------------------------------------
// Public interfaces
// ---------------------------------------------------------------------------

export interface TokenProvider {
  getIdToken(): Promise<string | null>;
}

export interface HttpClient {
  get<T>(path: string): Promise<T>;
  post<T>(path: string, body?: unknown): Promise<T>;
  patch<T>(path: string, body?: unknown): Promise<T>;
  put<T>(path: string, body?: unknown): Promise<T>;
  del(path: string): Promise<void>;
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

// Backstop so a stalled request can never hang a screen forever (e.g. the
// task-runtime spinner). Generous on purpose: the runtime POST runs an LLM +
// TTS call server-side, so normal requests stay well under it while a true
// stall still aborts instead of spinning indefinitely.
const DEFAULT_TIMEOUT_MS = 90_000;

export function createHttpClient(opts: {
  baseUrl: string;
  tokens: TokenProvider;
  /**
   * Invoked once when a request comes back 401. Should repair auth (e.g. mint a
   * fresh guest session) and resolve `true` if the caller should replay the
   * request, or `false` to surface the 401. Implementations must be
   * single-flight so concurrent 401s don't trigger multiple recoveries.
   */
  reauth?: () => Promise<boolean>;
  /** Per-request abort deadline; defaults to {@link DEFAULT_TIMEOUT_MS}. */
  timeoutMs?: number;
}): HttpClient {
  const { baseUrl, tokens, reauth, timeoutMs = DEFAULT_TIMEOUT_MS } = opts;

  async function buildHeaders(hasBody: boolean): Promise<HeadersInit> {
    const headers: Record<string, string> = {};

    if (hasBody) {
      headers['Content-Type'] = 'application/json';
    }

    const idToken = await tokens.getIdToken();
    if (idToken != null) {
      headers['Authorization'] = `Bearer ${idToken}`;
    }

    return headers;
  }

  async function request<T>(
    method: string,
    path: string,
    body?: unknown,
    isRetry = false,
  ): Promise<T> {
    const url = baseUrl + path;
    const hasBody = body !== undefined;

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    let response: Response;
    try {
      response = await fetch(url, {
        method,
        headers: await buildHeaders(hasBody),
        body: hasBody ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
    } catch (e) {
      throw AppError.from(e);
    } finally {
      clearTimeout(timer);
    }

    // A 401 means our token is stale or absent. Give the injected reauth hook
    // one chance to repair auth (mint a fresh guest session), then replay the
    // request exactly once. The isRetry guard prevents an infinite loop if the
    // replayed request 401s again (e.g. the backend is genuinely unreachable).
    if (response.status === 401 && !isRetry && reauth) {
      if (await reauth()) {
        return request<T>(method, path, body, true);
      }
    }

    if (!response.ok) {
      let errorBody: unknown = null;
      try {
        errorBody = await response.json();
      } catch {
        // ignore parse failures — fromHttp handles null body
      }
      throw AppError.fromHttp(response.status, errorBody);
    }

    // 204 No Content (or empty body) — return undefined cast for void callers
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return undefined as unknown as T;
    }

    // Guard against truly empty bodies (e.g. 200 with no content)
    const text = await response.text();
    if (!text) {
      return undefined as unknown as T;
    }

    return JSON.parse(text) as T;
  }

  return {
    get<T>(path: string): Promise<T> {
      return request<T>('GET', path);
    },
    post<T>(path: string, body?: unknown): Promise<T> {
      return request<T>('POST', path, body);
    },
    patch<T>(path: string, body?: unknown): Promise<T> {
      return request<T>('PATCH', path, body);
    },
    put<T>(path: string, body?: unknown): Promise<T> {
      return request<T>('PUT', path, body);
    },
    async del(path: string): Promise<void> {
      await request<void>('DELETE', path);
    },
  };
}
