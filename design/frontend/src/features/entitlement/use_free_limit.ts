/**
 * Free-limit view-model (small by design).
 *
 * The daily free-limit is enforced by the backend and returned INLINE on task
 * start/complete (`FreeLimit`). This hook does NOT recompute a remaining count
 * client-side — the backend value is authoritative. It only interprets a given
 * `FreeLimit` and opens the paywall when the backend says so.
 */

import { useCallback } from 'react';
import { useUiStore } from '@/state/stores/ui_store';
import { useEntitlement } from '@/features/entitlement/use_entitlement';
import type { FreeLimit } from '@/types/models';

export function useFreeLimit() {
  const { isWittyPlus } = useEntitlement();
  const openPaywall = useUiStore((state) => state.openPaywall);

  /**
   * Interpret a backend free-limit (from start/complete). When the backend
   * flags `shouldPaywall`, open the paywall. Returns whether it was triggered.
   */
  const handleFreeLimit = useCallback(
    (freeLimit: FreeLimit | null | undefined, reason = 'free_limit_reached'): boolean => {
      if (freeLimit?.shouldPaywall) {
        openPaywall(reason);
        return true;
      }
      return false;
    },
    [openPaywall],
  );

  return { isWittyPlus, handleFreeLimit };
}
