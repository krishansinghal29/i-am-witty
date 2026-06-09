/**
 * Entitlement ACTION guard (not a route guard).
 *
 * Exposes `useEntitlementGate()` for call sites that begin a gated action (e.g.
 * starting a task). It decides whether to open the paywall sheet or proceed.
 *
 * NOTE: the authoritative free-limit count is returned inline by `startTask` /
 * `completeTask`; this gate only decides whether to open the paywall sheet vs.
 * proceed — it does not itself track or enforce usage counts.
 */

import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import { useUiStore } from '@/state/stores/ui_store';
import type { FreeLimit } from '@/types/models';

export function useEntitlementGate() {
  const api = useRiffyApi();
  const access = useQuery({
    queryKey: queryKeys.access,
    queryFn: () => api.getAccess(),
  });
  const openPaywall = useUiStore((s) => s.openPaywall);

  return {
    isRiffyPlus: access.data?.isRiffyPlus ?? false,
    access: access.data ?? null,
    isLoading: access.isLoading,
    guardStart(freeLimit?: FreeLimit): boolean {
      if (freeLimit && freeLimit.shouldPaywall) {
        openPaywall(freeLimit.reason ?? undefined);
        return false;
      }
      return true;
    },
  };
}
