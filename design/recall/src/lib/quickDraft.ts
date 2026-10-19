/**
 * The unsent Quick add text, kept in this browser so a reload or a detour to
 * the full form doesn't lose it. Storage can be blocked, so every access is
 * guarded and failures just mean nothing is remembered.
 */

const STORAGE_KEY = 'riffy_recall_quick_text';

export function loadQuickDraft(): string {
  try {
    return window.localStorage.getItem(STORAGE_KEY) ?? '';
  } catch {
    return '';
  }
}

export function saveQuickDraft(text: string): void {
  try {
    if (text) window.localStorage.setItem(STORAGE_KEY, text);
    else window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Not remembered; nothing else to do.
  }
}

export function clearQuickDraft(): void {
  saveQuickDraft('');
}
