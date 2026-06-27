/**
 * Today's-plan view-model.
 *
 * Reads the bundled `/v1/home` response (shared, via `queryKeys.home`, with
 * {@link useProgressSummary} so it is fetched once) and selects just the daily
 * plan. Plan items only carry a `taskId`, so title/description/duration/etc. are
 * enriched from the cached catalog (`queryKeys.catalog`) AND lessons
 * (`queryKeys.lessons`) — lessons live in a separate endpoint, so without them
 * the plan's lesson items would fall back to a calm generic label.
 */

import { useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useHistory } from 'react-router-dom';
import { useRiffyApi } from '@/app/providers';
import { useFreeLimit } from '@/features/entitlement/use_free_limit';
import { queryKeys } from '@/state/query_keys';
import type { CatalogItem, DailyPlan, HomeView, PlanItemStatus } from '@/types/models';

/** Coarse task kind used to differentiate plan tiles (label + icon). */
export type PlanItemKind = 'lesson' | 'exercise';

/** task_type_id of audio lessons — the rest of the plan is exercises. */
const LESSON_TASK_TYPE_ID = 'lesson';

/** A plan item enriched with task display metadata for the screen. */
export interface PlanItemView {
  /** Daily-plan item id (passed back to the runtime as `dailyPlanItemId`). */
  id: string;
  taskId: string;
  position: number;
  status: PlanItemStatus;
  /** Lesson vs exercise, or null while the task is still unresolved. */
  kind: PlanItemKind | null;
  title: string;
  description: string | null;
  durationSeconds: number | null;
  thumbnailKey: string | null;
  /** Slug, used as a stable fallback tint key for the thumbnail. */
  slug: string | null;
  /** Premium task the caller can't start yet (shows a Riffy+ badge). */
  isLocked: boolean;
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

  // Best-effort enrichment; never blocks the plan from rendering. Both the
  // exercise catalog and the (separate) lessons endpoint are merged so every
  // plan item — exercise or lesson — resolves to real display metadata.
  const catalog = useQuery({
    queryKey: queryKeys.catalog,
    queryFn: () => api.getCatalog(),
  });
  const lessons = useQuery({
    queryKey: queryKeys.lessons,
    queryFn: () => api.getLessons(),
  });

  const items = useMemo<PlanItemView[]>(() => {
    const plan = home.data;
    if (!plan) return [];

    const byTaskId = new Map<string, CatalogItem>();
    for (const entry of [...(catalog.data ?? []), ...(lessons.data ?? [])]) {
      byTaskId.set(entry.task.id, entry);
    }

    const ordered = [...plan.items].sort((a, b) => a.position - b.position);
    const nextUpId = pickNextUpId(ordered);

    return ordered.map((item) => {
      const entry = byTaskId.get(item.taskId);
      const task = entry?.task;
      return {
        id: item.id,
        taskId: item.taskId,
        position: item.position,
        status: item.status,
        kind: task
          ? task.taskTypeId === LESSON_TASK_TYPE_ID
            ? 'lesson'
            : 'exercise'
          : null,
        title: task?.title ?? 'Practice',
        description: task?.description ?? null,
        durationSeconds: task?.durationSeconds ?? null,
        thumbnailKey: task?.thumbnailKey ?? null,
        slug: task?.slug ?? null,
        isLocked: entry?.isLocked ?? false,
        isNextUp: item.id === nextUpId,
      };
    });
  }, [home.data, catalog.data, lessons.data]);

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
