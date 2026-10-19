/**
 * Anonymous learner id for public practice: a random UUID kept in this browser.
 * Storage can be blocked (private windows), so fall back to an in-memory id.
 */

const STORAGE_KEY = 'riffy_recall_learner';

let memoryId: string | null = null;

function newId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  // RFC 4122 v4 from getRandomValues for older browsers.
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

export function getLearnerId(): string {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    const id = memoryId ?? newId();
    window.localStorage.setItem(STORAGE_KEY, id);
    memoryId = id;
    return id;
  } catch {
    memoryId ??= newId();
    return memoryId;
  }
}
