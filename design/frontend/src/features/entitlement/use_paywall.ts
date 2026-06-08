/**
 * Paywall view-model.
 *
 * Loads live offerings through the {@link SubscriptionGateway} port (RevenueCat
 * native on device, Web Billing on the browser — keyed by `queryKeys.offerings`)
 * and exposes `purchase(pkg)` / `restore()`. On success both invalidate the
 * backend access state (`queryKeys.access`) — the authoritative entitlement —
 * plus the offerings cache, then the UI re-reads the truth.
 */

import { useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useIntegrations } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type {
  EntitlementSnapshot,
  SubscriptionPackage,
} from '@/integrations/ports/subscription_gateway';

export interface UsePaywallOptions {
  /** Only fetch offerings when the paywall is actually visible. */
  enabled?: boolean;
}

export function usePaywall(options: UsePaywallOptions = {}) {
  const { enabled = true } = options;
  const { subscriptions } = useIntegrations();
  const queryClient = useQueryClient();

  const offeringsQuery = useQuery({
    queryKey: queryKeys.offerings,
    queryFn: () => subscriptions.getOfferings(),
    enabled,
    staleTime: 5 * 60 * 1000,
  });

  const invalidate = useCallback(async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.access }),
      queryClient.invalidateQueries({ queryKey: queryKeys.offerings }),
    ]);
  }, [queryClient]);

  const purchaseMutation = useMutation<EntitlementSnapshot, unknown, SubscriptionPackage>({
    mutationFn: (pkg) => subscriptions.purchasePackage(pkg),
    onSuccess: invalidate,
  });

  const restoreMutation = useMutation<EntitlementSnapshot, unknown, void>({
    mutationFn: () => subscriptions.restorePurchases(),
    onSuccess: invalidate,
  });

  // The catalog/paywall typically exposes a single (current) offering.
  const packages = offeringsQuery.data?.[0]?.packages ?? [];

  return {
    offerings: offeringsQuery.data ?? [],
    packages,
    isLoading: offeringsQuery.isLoading,
    isError: offeringsQuery.isError,
    isEmpty: !offeringsQuery.isLoading && packages.length === 0,
    refetch: offeringsQuery.refetch,
    purchase: (pkg: SubscriptionPackage) => purchaseMutation.mutateAsync(pkg),
    restore: () => restoreMutation.mutateAsync(),
    isPurchasing: purchaseMutation.isPending,
    isRestoring: restoreMutation.isPending,
    purchaseError: purchaseMutation.error,
    restoreError: restoreMutation.error,
  };
}
