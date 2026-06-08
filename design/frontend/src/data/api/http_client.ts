/**
 * Minimal typed HTTP client used by WittyApi.
 *
 * Auth strategy (in priority order):
 *   1. Firebase id-token  → Authorization: Bearer <token>
 *   2. Guest token        → X-Guest-Token: <token>
 *   3. No header
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
  getGuestToken(): Promise<string | null>;
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

export function createHttpClient(opts: {
  baseUrl: string;
  tokens: TokenProvider;
}): HttpClient {
  const { baseUrl, tokens } = opts;

  async function buildHeaders(hasBody: boolean): Promise<HeadersInit> {
    const headers: Record<string, string> = {};

    if (hasBody) {
      headers['Content-Type'] = 'application/json';
    }

    const idToken = await tokens.getIdToken();
    if (idToken != null) {
      headers['Authorization'] = `Bearer ${idToken}`;
    } else {
      const guestToken = await tokens.getGuestToken();
      if (guestToken != null) {
        headers['X-Guest-Token'] = guestToken;
      }
    }

    return headers;
  }

  async function request<T>(
    method: string,
    path: string,
    body?: unknown,
  ): Promise<T> {
    const url = baseUrl + path;
    const hasBody = body !== undefined;

    let response: Response;
    try {
      response = await fetch(url, {
        method,
        headers: await buildHeaders(hasBody),
        body: hasBody ? JSON.stringify(body) : undefined,
      });
    } catch (e) {
      throw AppError.from(e);
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
