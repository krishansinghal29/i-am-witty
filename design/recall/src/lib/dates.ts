/** The browser's local calendar date as YYYY-MM-DD (not UTC). */
export function localDate(date: Date = new Date()): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function parse(isoDate: string): Date {
  const [y, m, d] = isoDate.split('-').map(Number);
  return new Date(y, m - 1, d);
}

/** Single-letter weekday for a YYYY-MM-DD date, e.g. "M". */
export function weekdayLetter(isoDate: string): string {
  return 'SMTWTFS'[parse(isoDate).getDay()];
}

/** Short header date, e.g. "Mon 19 Oct". */
export function headerDate(date: Date = new Date()): string {
  return date.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' });
}
