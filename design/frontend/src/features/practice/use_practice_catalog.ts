/**
 * Practice-catalog view-model.
 *
 * Reads `/v1/catalog` (`queryKeys.catalog`) and exposes the items plus a small
 * client-side access-tier filter (all / free / premium). Tap-to-open and
 * paywall decisions live in the screen; this hook owns data + filtering only.
 */

import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type { CatalogItem } from '@/types/models';

/** Client-side filter over the catalog by access tier. */
export type CatalogFilter = 'all' | 'free' | 'premium';

export function usePracticeCatalog() {
  const api = useRiffyApi();
  const [filter, setFilter] = useState<CatalogFilter>('all');

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: queryKeys.catalog,
    queryFn: () => api.getCatalog(),
  });

  const items = useMemo<CatalogItem[]>(() => {
    const all = data ?? [];
    switch (filter) {
      case 'free':
        return all.filter((item) => !item.requiresPremium);
      case 'premium':
        return all.filter((item) => item.requiresPremium);
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
