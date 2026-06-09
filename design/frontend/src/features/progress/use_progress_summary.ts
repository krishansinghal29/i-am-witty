/**
 * Progress-summary view-model.
 *
 * Reads the bundled `/v1/home` response (shared, via `queryKeys.home`, with
 * {@link useTodayPlan} so it is fetched once) and selects the progress block:
 * streak counts, completed count, and a Su–Sa week model derived from the
 * current streak + last activity date for the `WeekStrip`.
 */

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type { WeekDay } from '@/components/ui';
import type { HomeView, Progress } from '@/types/models';

const MS_PER_DAY = 24 * 60 * 60 * 1000;

/** Midnight (local) of the given date. */
function startOfDay(date: Date): Date {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

/**
 * Build a Su–Sa week model. Days inside the current streak window (ending on
 * `lastActivityDate`) render as done; the current day is highlighted; other
 * past days are missed and future days are upcoming.
 */
function buildWeek(progress: Progress | null): WeekDay[] {
  const today = startOfDay(new Date());
  const todayIndex = today.getDay(); // 0 = Sunday
  const sunday = new Date(today.getTime() - todayIndex * MS_PER_DAY);

  const doneDays = new Set<number>();
  if (progress?.lastActivityDate) {
    const last = startOfDay(new Date(progress.lastActivityDate));
    const streak = Math.max(progress.currentStreakCount, 0);
    for (let i = 0; i < streak; i += 1) {
      doneDays.add(last.getTime() - i * MS_PER_DAY);
    }
  }

  return Array.from({ length: 7 }, (_, i): WeekDay => {
    const time = sunday.getTime() + i * MS_PER_DAY;
    if (time === today.getTime()) return { state: 'today' };
    if (time > today.getTime()) return { state: 'upcoming' };
    return { state: doneDays.has(time) ? 'done' : 'missed' };
  });
}

export function useProgressSummary() {
  const api = useRiffyApi();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: queryKeys.home,
    queryFn: () => api.getHome(),
    select: (home: HomeView): Progress => home.progress,
  });

  const week = useMemo(() => buildWeek(data ?? null), [data]);

  return {
    progress: data ?? null,
    currentStreak: data?.currentStreakCount ?? 0,
    longestStreak: data?.longestStreakCount ?? 0,
    completedCount: data?.completedTaskCount ?? 0,
    week,
    isLoading,
    isError,
    refetch,
  };
}
