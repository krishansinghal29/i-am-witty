/**
 * Entitlement view-model.
 *
 * Reads the backend's authoritative access state (`/v1/me/access`, keyed by
 * `queryKeys.access`) and exposes whether the user has Riffy+. The backend —
 * not the store SDK — is the source of truth for entitlement.
 */

import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';

export function useEntitlement() {
  const api = useRiffyApi();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: queryKeys.access,
    queryFn: () => api.getAccess(),
  });

  return {
    access: data ?? null,
    isRiffyPlus: data?.isRiffyPlus ?? false,
    entitlements: data?.entitlements ?? [],
    isLoading,
    isError,
    refetch,
  };
}
