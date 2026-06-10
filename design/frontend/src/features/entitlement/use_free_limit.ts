/**
 * Free-limit view-model (small by design).
 *
 * The daily free-limit is enforced by the backend and returned INLINE on task
 * start/complete (`FreeLimit`) and bundled on `/v1/home`. This hook does NOT
 * recompute a remaining count client-side — the backend value is authoritative.
 * It interprets those payloads and opens the paywall when the backend says so.
 */

import { useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { AppError } from '@/data/errors/app_error';
import { useEntitlement } from '@/features/entitlement/use_entitlement';
import { queryKeys } from '@/state/query_keys';
import { useUiStore } from '@/state/stores/ui_store';
import type { FreeLimit, HomeView } from '@/types/models';

export function useFreeLimit() {
  const api = useRiffyApi();
  const queryClient = useQueryClient();
  const { isRiffyPlus } = useEntitlement();
  const openPaywall = useUiStore((state) => state.openPaywall);

  // Prefetch home so practice (and other tabs) have today's free-limit gate.
  useQuery({
    queryKey: queryKeys.home,
    queryFn: () => api.getHome(),
    enabled: !isRiffyPlus,
    staleTime: 30_000,
  });

  /**
   * Interpret a backend free-limit (from start/complete/home). When the backend
   * flags `shouldPaywall`, open the paywall. Returns whether it was triggered.
   */
  const handleFreeLimit = useCallback(
    (freeLimit: FreeLimit | null | undefined, reason = 'free_limit_reached'): boolean => {
      if (freeLimit?.shouldPaywall) {
        openPaywall(freeLimit.reason ?? reason);
        return true;
      }
      return false;
    },
    [openPaywall],
  );

  /** Map a 402 / paywall_required API error to the subscription sheet. */
  const handlePaywallRequired = useCallback(
    (error: unknown): boolean => {
      const appError = AppError.from(error);
      if (appError.code === 'paywall_required') {
        openPaywall(appError.reason ?? 'free_limit_reached');
        return true;
      }
      return false;
    },
    [openPaywall],
  );

  /**
   * Pre-navigation gate: read cached `/v1/home` free-limit before pushing the
   * runtime route. Fail-open when home is not loaded yet — runtime 402 handling
   * remains the hard backstop.
   */
  const gateTaskStart = useCallback((): boolean => {
    if (isRiffyPlus) return true;

    const home = queryClient.getQueryData<HomeView>(queryKeys.home);
    if (!home?.freeLimit) return true;

    if (home.freeLimit.shouldPaywall) {
      openPaywall(home.freeLimit.reason ?? 'free_limit_reached');
      return false;
    }
    return true;
  }, [isRiffyPlus, openPaywall, queryClient]);

  return {
    isRiffyPlus,
    handleFreeLimit,
    handlePaywallRequired,
    gateTaskStart,
  };
}
