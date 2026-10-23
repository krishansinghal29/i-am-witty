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

/** Local hour a new Recall day starts; before it, it's still the previous day. */
export const RECALL_DAY_START_HOUR = 5;

/**
 * The Recall day for `now`: the local calendar date, except that the small
 * hours (before {@link RECALL_DAY_START_HOUR}) still count as the day before,
 * so a late-night session doesn't use up the next day's cards.
 */
export function recallDayString(now: Date = new Date()): string {
  const day = new Date(now);
  if (day.getHours() < RECALL_DAY_START_HOUR) day.setDate(day.getDate() - 1);
  return localDateString(day);
}
