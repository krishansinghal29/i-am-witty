/**
 * Tiny Result<T, E> type for explicit error handling without exceptions.
 */

import type { AppError } from '@/data/errors/app_error';

export type Result<T, E = AppError> =
  | { ok: true; value: T }
  | { ok: false; error: E };

/** Wrap a successful value in a Result. */
export function ok<T>(value: T): { ok: true; value: T } {
  return { ok: true, value };
}

/** Wrap an error in a Result. */
export function err<E>(error: E): { ok: false; error: E } {
  return { ok: false, error };
}

/** Type guard — narrows `r` to the success variant. */
export function isOk<T, E>(r: Result<T, E>): r is { ok: true; value: T } {
  return r.ok === true;
}
