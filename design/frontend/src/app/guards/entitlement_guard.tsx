/**
 * Entitlement ACTION guard (not a route guard).
 *
 * Thin wrapper around {@link useFreeLimit} for call sites that begin a gated
 * action (e.g. starting a task). Prefer importing `useFreeLimit` directly.
 */

import type { FreeLimit } from '@/types/models';
import { useFreeLimit } from '@/features/entitlement/use_free_limit';

export function useEntitlementGate() {
  const { isRiffyPlus, gateTaskStart, handleFreeLimit } = useFreeLimit();

  return {
    isRiffyPlus,
    isLoading: false,
    guardStart(freeLimit?: FreeLimit): boolean {
      if (freeLimit?.shouldPaywall) {
        return !handleFreeLimit(freeLimit);
      }
      return gateTaskStart();
    },
  };
}
