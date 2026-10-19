/**
 * The device-local calendar date as "YYYY-MM-DD" (not UTC), which is what the
 * backend's day-based schedules (Recall) key on.
 */
export function localDateString(date: Date = new Date()): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}
