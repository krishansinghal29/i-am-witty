/**
 * Remembers whether this browser has a Firebase session, so public practice can
 * skip loading Firebase entirely for anonymous visitors.
 */

const STORAGE_KEY = 'riffy_recall_signed_in';

export function hasSignedInHint(): boolean {
  try {
    return window.localStorage.getItem(STORAGE_KEY) === '1';
  } catch {
    return false;
  }
}

export function rememberSignedIn(signedIn: boolean): void {
  try {
    if (signedIn) window.localStorage.setItem(STORAGE_KEY, '1');
    else window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Storage blocked: public calls just go out without a token.
  }
}
