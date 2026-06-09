/**
 * Paywall view-model.
 *
 * Loads live offerings through the {@link SubscriptionGateway} port (RevenueCat
 * native on device — keyed by `queryKeys.offerings`) and exposes `purchase(pkg)`
 * / `restore()`. On success it asks the backend to pull the purchase from
 * RevenueCat immediately (`syncAccess`) rather than waiting on the webhook, then
 * primes the access cache (`queryKeys.access`) — the authoritative entitlement —
 * so the UI reflects the new state at once.
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
  const { subscriptions, api } = useIntegrations();
  const queryClient = useQueryClient();

  const offeringsQuery = useQuery({
    queryKey: queryKeys.offerings,
    queryFn: () => subscriptions.getOfferings(),
    enabled,
    staleTime: 5 * 60 * 1000,
  });

  const reconcile = useCallback(async () => {
    // Force the backend to pull the just-made purchase from RevenueCat now, then
    // prime the access cache with the fresh truth. Falls back to invalidation if
    // the sync call fails — the webhook will reconcile shortly after.
    try {
      const access = await api.syncAccess();
      queryClient.setQueryData(queryKeys.access, access);
    } catch {
      await queryClient.invalidateQueries({ queryKey: queryKeys.access });
    }
    await queryClient.invalidateQueries({ queryKey: queryKeys.offerings });
  }, [api, queryClient]);

  const purchaseMutation = useMutation<EntitlementSnapshot, unknown, SubscriptionPackage>({
    mutationFn: (pkg) => subscriptions.purchasePackage(pkg),
    onSuccess: reconcile,
  });

  const restoreMutation = useMutation<EntitlementSnapshot, unknown, void>({
    mutationFn: () => subscriptions.restorePurchases(),
    onSuccess: reconcile,
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
