/**
 * Session hook (login-only).
 *
 * A session exists only for a user who signed in AND finished onboarding. We
 * treat the persisted backend `app_user_id` as that "onboarded" marker: it is
 * written exactly once, by onboarding completion. So:
 *   - Firebase session + persisted app_user_id → authenticated session
 *   - otherwise (no Firebase user, or signed in but not yet completed) → null,
 *     which routes the app to onboarding.
 *
 * There are no guests and no auto-minting; onboarding is the only path that
 * creates a user.
 */

import { useQuery } from '@tanstack/react-query';
import { useIntegrations, STORAGE_KEYS } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type { Session } from '@/types/models';

export function useSession() {
  const { auth, secureStore } = useIntegrations();

  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.session,
    queryFn: async (): Promise<Session | null> => {
      const fb = await auth.getSession();
      if (fb === null) return null;
      const backendId = await secureStore.get(STORAGE_KEYS.appUserId);
      if (!backendId) return null;
      // Firebase reports its uid as appUserId; the backend app_user_id is the
      // stable UUID both the backend and RevenueCat match on — prefer it.
      return { ...fb, appUserId: backendId };
    },
    // The session is durable; don't refetch or retry-storm.
    staleTime: Infinity,
    retry: false,
  });

  return {
    session: data ?? null,
    isLoading,
    isError,
    isAuthenticated: data != null,
  };
}
