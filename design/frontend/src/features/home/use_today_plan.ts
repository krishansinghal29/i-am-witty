/**
 * Today's-plan view-model.
 *
 * Reads the bundled `/v1/home` response (shared, via `queryKeys.home`, with
 * {@link useProgressSummary} so it is fetched once) and selects just the daily
 * plan. Plan items only carry a `taskId`, so titles/durations are enriched from
 * the cached catalog (`queryKeys.catalog`) when available, falling back to a
 * calm generic label otherwise.
 */

import { useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useHistory } from 'react-router-dom';
import { useRiffyApi } from '@/app/providers';
import { useFreeLimit } from '@/features/entitlement/use_free_limit';
import { queryKeys } from '@/state/query_keys';
import type { CatalogItem, DailyPlan, HomeView, PlanItemStatus } from '@/types/models';

/** A plan item enriched with task display metadata for the screen. */
export interface PlanItemView {
  /** Daily-plan item id (passed back to the runtime as `dailyPlanItemId`). */
  id: string;
  taskId: string;
  position: number;
  status: PlanItemStatus;
  title: string;
  durationSeconds: number | null;
  thumbnailKey: string | null;
  /** True for the single highlighted "Next up" item. */
  isNextUp: boolean;
}

const TERMINAL: ReadonlySet<PlanItemStatus> = new Set(['completed', 'missed']);

/** Pick the single "Next up": the current item, else the first unfinished one. */
function pickNextUpId(items: { id: string; status: PlanItemStatus }[]): string | null {
  const current = items.find((i) => i.status === 'current');
  if (current) return current.id;
  const upcoming = items.find((i) => !TERMINAL.has(i.status));
  return upcoming?.id ?? null;
}

export function useTodayPlan() {
  const api = useRiffyApi();
  const history = useHistory();
  const { gateTaskStart } = useFreeLimit();

  const home = useQuery({
    queryKey: queryKeys.home,
    queryFn: () => api.getHome(),
    select: (data: HomeView): DailyPlan => data.plan,
  });

  // Best-effort enrichment; never blocks the plan from rendering.
  const catalog = useQuery({
    queryKey: queryKeys.catalog,
    queryFn: () => api.getCatalog(),
  });

  const items = useMemo<PlanItemView[]>(() => {
    const plan = home.data;
    if (!plan) return [];

    const byTaskId = new Map<string, CatalogItem>();
    for (const entry of catalog.data ?? []) {
      byTaskId.set(entry.task.id, entry);
    }

    const ordered = [...plan.items].sort((a, b) => a.position - b.position);
    const nextUpId = pickNextUpId(ordered);

    return ordered.map((item) => {
      const task = byTaskId.get(item.taskId)?.task;
      return {
        id: item.id,
        taskId: item.taskId,
        position: item.position,
        status: item.status,
        title: task?.title ?? 'Practice',
        durationSeconds: task?.durationSeconds ?? null,
        thumbnailKey: task?.thumbnailKey ?? null,
        isNextUp: item.id === nextUpId,
      };
    });
  }, [home.data, catalog.data]);

  const nextUp = useMemo(
    () => items.find((item) => item.isNextUp) ?? null,
    [items],
  );

  const openTask = useCallback(
    (item: { id: string; taskId: string }) => {
      if (!gateTaskStart()) return;

      const params = new URLSearchParams({
        source: 'daily_plan',
        dailyPlanItemId: item.id,
      });
      history.push(`/task/${item.taskId}?${params.toString()}`);
    },
    [gateTaskStart, history],
  );

  return {
    items,
    nextUp,
    openTask,
    isLoading: home.isLoading,
    isError: home.isError,
    refetch: home.refetch,
  };
}
