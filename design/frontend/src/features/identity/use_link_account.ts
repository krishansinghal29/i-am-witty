/**
 * Guest -> authenticated linking.
 *
 * Signs in with Firebase (Apple/Google) through the {@link AuthGateway} port,
 * takes the resulting Firebase ID token, and calls `POST /v1/auth/link` so the
 * backend merges the guest's progress into the authenticated account. On success
 * it invalidates session / home / access (the surfaces the merge touches).
 *
 * If Firebase keys are absent the gateway throws a friendly `AppError`; callers
 * surface `error` and keep a "Not now" path available.
 */

import { useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useIntegrations, STORAGE_KEYS } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import { AppError } from '@/data/errors/app_error';
import type { Session } from '@/types/models';

export type AuthProvider = 'apple' | 'google';

export interface UseLinkAccount {
  linkWithApple: () => Promise<Session>;
  linkWithGoogle: () => Promise<Session>;
  isLinking: boolean;
  error: unknown;
  reset: () => void;
}

export function useLinkAccount(): UseLinkAccount {
  const { auth, api, secureStore } = useIntegrations();
  const queryClient = useQueryClient();

  const mutation = useMutation<Session, unknown, AuthProvider>({
    mutationFn: async (provider) => {
      if (provider === 'apple') {
        await auth.signInWithApple();
      } else {
        await auth.signInWithGoogle();
      }
      const idToken = await auth.getIdToken();
      if (!idToken) {
        throw new AppError({
          code: 'unauthorized',
          userMessage: 'Sign-in didn’t complete. Please try again.',
          reason: 'missing_id_token',
        });
      }
      return api.linkAccount(idToken);
    },
    onSuccess: async (session) => {
      // The backend preserves app_user_id across the guest→auth merge. Persist
      // it so the authenticated session resolves to the backend UUID (which
      // RevenueCat and the backend match on) rather than the Firebase uid.
      if (session.appUserId) {
        await secureStore.set(STORAGE_KEYS.appUserId, session.appUserId);
      }
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.session }),
        queryClient.invalidateQueries({ queryKey: queryKeys.home }),
        queryClient.invalidateQueries({ queryKey: queryKeys.access }),
      ]);
    },
  });

  const linkWithApple = useCallback(
    () => mutation.mutateAsync('apple'),
    [mutation],
  );
  const linkWithGoogle = useCallback(
    () => mutation.mutateAsync('google'),
    [mutation],
  );

  return {
    linkWithApple,
    linkWithGoogle,
    isLinking: mutation.isPending,
    error: mutation.error,
    reset: mutation.reset,
  };
}
