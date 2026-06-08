/**
 * Utilities for respecting the OS-level "prefers-reduced-motion" accessibility setting.
 */

const QUERY = '(prefers-reduced-motion: reduce)';

/**
 * Returns `true` when the user has requested reduced motion.
 * Returns `false` in environments without `window.matchMedia` (e.g. SSR/test).
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false;
  }
  return window.matchMedia(QUERY).matches;
}

/**
 * Subscribes `cb` to reduced-motion preference changes.
 * Returns an unsubscribe function.
 * Returns a no-op unsubscribe in environments without `window.matchMedia`.
 */
export function onReducedMotionChange(
  cb: (reduced: boolean) => void,
): () => void {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return () => { /* no-op */ };
  }

  const mql = window.matchMedia(QUERY);
  const handler = (event: MediaQueryListEvent) => cb(event.matches);

  mql.addEventListener('change', handler);

  return () => {
    mql.removeEventListener('change', handler);
  };
}
