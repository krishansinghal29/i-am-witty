/**
 * Minimal JSON client for the Recall endpoints.
 *
 * Public calls always send X-Recall-Learner, plus the Firebase ID token when
 * someone is signed in on this browser. Admin calls require the token.
 *
 * Error bodies come in three shapes: {"error": reason} (application errors),
 * {"detail": "..."} (HTTP errors) and {"detail": [...]} (request validation).
 */

import { getLearnerId } from '@/lib/learner';
import { hasSignedInHint } from '@/lib/signedInHint';

const BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/+$/, '');

export class ApiError extends Error {
  readonly status: number;
  /** Machine reason from the backend, e.g. "hint_required", when there is one. */
  readonly reason: string | null;

  constructor(status: number, reason: string | null, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.reason = reason;
  }
}

function friendlyMessage(status: number, reason: string | null): string {
  if (status === 0) return "Couldn't reach Recall. Check your connection and try again.";
  if (status === 401) return 'Your sign-in expired. Sign in again.';
  if (status === 403) return "This account can't edit Recall.";
  if (status === 404) return "That item doesn't exist anymore.";
  if (status === 409) return 'A cue with that text already exists.';
  if (status === 422 && reason) return `Check the form: ${reason.replace(/_/g, ' ')}.`;
  if (status === 422) return 'Some fields need fixing.';
  if (status >= 500) return 'Something went wrong on our side. Try again in a moment.';
  return 'Something went wrong. Try again.';
}

type Audience = 'public' | 'admin';

async function request<T>(
  method: 'GET' | 'POST' | 'PATCH',
  path: string,
  audience: Audience,
  body?: unknown,
): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (audience === 'public') headers['X-Recall-Learner'] = getLearnerId();

  // Firebase loads only for admin calls or when this browser has signed in
  // before, so anonymous visitors never wait on it.
  let token: string | null = null;
  if (audience === 'admin' || hasSignedInHint()) {
    const { currentIdToken } = await import('@/lib/firebase');
    token = await currentIdToken();
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  } else if (audience === 'admin') {
    throw new ApiError(401, 'unauthenticated', friendlyMessage(401, null));
  }

  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, 'network', friendlyMessage(0, null));
  }

  const text = await response.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const payload = (data ?? {}) as { error?: unknown; detail?: unknown };
    const reason =
      typeof payload.error === 'string'
        ? payload.error
        : typeof payload.detail === 'string'
          ? payload.detail
          : null;
    throw new ApiError(response.status, reason, friendlyMessage(response.status, reason));
  }
  return data as T;
}

export const http = {
  publicGet: <T>(path: string) => request<T>('GET', path, 'public'),
  publicPost: <T>(path: string, body: unknown) => request<T>('POST', path, 'public', body),
  adminGet: <T>(path: string) => request<T>('GET', path, 'admin'),
  adminPost: <T>(path: string, body: unknown) => request<T>('POST', path, 'admin', body),
  adminPatch: <T>(path: string, body: unknown) => request<T>('PATCH', path, 'admin', body),
};

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Try again.';
}
