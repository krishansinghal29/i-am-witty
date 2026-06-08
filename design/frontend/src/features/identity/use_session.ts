/**
 * Session bootstrap hook (guest-first).
 *
 * Ensures a durable session exists before any authed query fires: it prefers an
 * authenticated Firebase session, falls back to a persisted guest token, and
 * otherwise mints a fresh guest session and persists its credentials.
 */

import { useQuery } from '@tanstack/react-query';
import { useIntegrations, STORAGE_KEYS } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type { Session } from '@/types/models';

export function useSession() {
  const { auth, secureStore, api } = useIntegrations();

  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.session,
    queryFn: async (): Promise<Session> => {
      // 1. Authenticated Firebase session takes precedence.
      const fb = await auth.getSession();
      if (fb !== null) {
        return fb;
      }

      // 2. Reconstruct a guest session from a persisted token, if present.
      const token = await secureStore.get(STORAGE_KEYS.guestToken);
      if (token) {
        return {
          appUserId: (await secureStore.get(STORAGE_KEYS.appUserId)) ?? '',
          status: 'guest',
          sessionToken: token,
          firebaseUid: null,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        };
      }

      // 3. No session yet — mint a fresh guest session and persist it.
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const s = await api.createGuestSession({ timezone: tz });
      if (s.sessionToken) {
        await secureStore.set(STORAGE_KEYS.guestToken, s.sessionToken);
      }
      await secureStore.set(STORAGE_KEYS.appUserId, s.appUserId);
      return s;
    },
    // The session is durable; don't refetch or retry-storm.
    staleTime: Infinity,
    retry: false,
  });

  return {
    session: data ?? null,
    isLoading,
    isError,
    isGuest: data?.status === 'guest',
    isAuthenticated: data?.status === 'authenticated',
  };
}
