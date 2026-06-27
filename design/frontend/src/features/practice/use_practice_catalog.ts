/**
 * Practice-catalog view-model.
 *
 * Exposes the practice library plus a client-side format filter. Roleplay and
 * standard exercises come from `/v1/catalog`; audio lessons live in their own
 * non-metered endpoint (`/v1/lessons`) and are fetched lazily the first time the
 * Lessons filter is opened. Tap-to-open and paywall decisions live in the
 * screen; this hook owns data + filtering only.
 */

import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type { CatalogItem } from '@/types/models';

/** task_type_id of the roleplay-version exercises (vs. the normal voice ones). */
const ROLEPLAY_TASK_TYPE_ID = 'roleplay';

/** Client-side filter over the practice library by content format. */
export type CatalogFilter = 'roleplay' | 'normal' | 'lessons';

export function usePracticeCatalog() {
  const api = useRiffyApi();
  const [filter, setFilter] = useState<CatalogFilter>('roleplay');
  const isLessons = filter === 'lessons';

  const catalogQuery = useQuery({
    queryKey: queryKeys.catalog,
    queryFn: () => api.getCatalog(),
  });
  const lessonsQuery = useQuery({
    queryKey: queryKeys.lessons,
    queryFn: () => api.getLessons(),
    enabled: isLessons,
  });

  const items = useMemo<CatalogItem[]>(() => {
    if (isLessons) return lessonsQuery.data ?? [];
    const all = catalogQuery.data ?? [];
    const isRoleplay = (item: CatalogItem) =>
      item.task.taskTypeId === ROLEPLAY_TASK_TYPE_ID;
    return filter === 'roleplay'
      ? all.filter(isRoleplay)
      : all.filter((item) => !isRoleplay(item));
  }, [isLessons, lessonsQuery.data, catalogQuery.data, filter]);

  const active = isLessons ? lessonsQuery : catalogQuery;

  return {
    items,
    totalCount: items.length,
    filter,
    setFilter,
    isLoading: active.isLoading,
    isError: active.isError,
    refetch: active.refetch,
  };
}
