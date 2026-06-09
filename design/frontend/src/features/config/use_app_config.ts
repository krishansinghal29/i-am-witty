/**
 * Remote app-config hook.
 *
 * Fetches `/v1/config` (no auth required) and exposes convenient slices for the
 * free-task limit, raw config values, and feature gates.
 */

import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';

export function useAppConfig() {
  const api = useRiffyApi();

  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.config,
    queryFn: () => api.getConfig(),
  });

  return {
    config: data ?? null,
    isLoading,
    isError,
    freeTaskLimit: data?.freeTaskLimit ?? null,
    values: data?.values ?? {},
    featureGates: data?.featureGates ?? [],
  };
}
