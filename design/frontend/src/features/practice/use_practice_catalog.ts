/**
 * Practice-catalog view-model.
 *
 * Reads `/v1/catalog` (`queryKeys.catalog`) and exposes the items plus a small
 * client-side format filter (roleplay-version / normal exercises). Tap-to-open
 * and paywall decisions live in the screen; this hook owns data + filtering
 * only.
 */

import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type { CatalogItem } from '@/types/models';

/** task_type_id of the roleplay-version exercises (vs. the normal voice ones). */
const ROLEPLAY_TASK_TYPE_ID = 'roleplay';

/** Client-side filter over the catalog by exercise format. */
export type CatalogFilter = 'roleplay' | 'normal';

export function usePracticeCatalog() {
  const api = useRiffyApi();
  const [filter, setFilter] = useState<CatalogFilter>('roleplay');

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: queryKeys.catalog,
    queryFn: () => api.getCatalog(),
  });

  const items = useMemo<CatalogItem[]>(() => {
    const all = data ?? [];
    const isRoleplay = (item: CatalogItem) =>
      item.task.taskTypeId === ROLEPLAY_TASK_TYPE_ID;
    switch (filter) {
      case 'roleplay':
        return all.filter(isRoleplay);
      case 'normal':
        return all.filter((item) => !isRoleplay(item));
      default:
        return all;
    }
  }, [data, filter]);

  return {
    items,
    totalCount: data?.length ?? 0,
    filter,
    setFilter,
    isLoading,
    isError,
    refetch,
  };
}
