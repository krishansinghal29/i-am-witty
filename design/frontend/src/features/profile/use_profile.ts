/**
 * Profile view-model — session identity + sign-out.
 *
 * Composes the existing session bootstrap ({@link useSession}) with a sign-out
 * mutation over the {@link AuthGateway} port. On sign-out the guest-merged
 * server state is no longer valid for the (now signed-out) identity, so we
 * invalidate the session, home (plan + progress) and access caches; TanStack
 * re-bootstraps a fresh (guest) session on the next read.
 *
 * Stats themselves are not fetched here — the screen reuses
 * `useProgressSummary` / `useEntitlement` directly.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useIntegrations, STORAGE_KEYS } from '@/app/providers';
import { useSession } from '@/features/identity/use_session';
import { queryKeys } from '@/state/query_keys';

export function useProfile() {
  const { auth, secureStore } = useIntegrations();
  const queryClient = useQueryClient();
  const { session, isAuthenticated, isLoading } = useSession();

  const signOutMutation = useMutation<void, unknown, void>({
    mutationFn: async () => {
      await auth.signOut();
      // Drop the "onboarded" marker so the app routes back to onboarding.
      await secureStore.remove(STORAGE_KEYS.appUserId);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.session }),
        queryClient.invalidateQueries({ queryKey: queryKeys.home }),
        queryClient.invalidateQueries({ queryKey: queryKeys.access }),
      ]);
    },
  });

  return {
    session,
    isAuthenticated,
    isLoadingSession: isLoading,
    signOut: () => signOutMutation.mutateAsync(),
    isSigningOut: signOutMutation.isPending,
    signOutError: signOutMutation.error,
  };
}
