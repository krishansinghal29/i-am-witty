/**
 * Onboarding view-model (login-only, client-side until completion).
 *
 * Two steps held in `onboarding_store`: pick a trigger (no network), then sign
 * in. Signing in is the single write of the whole flow: it authenticates with
 * Firebase, then `POST /v1/onboarding/complete` creates the user + onboarding
 * row and returns the session. We persist the backend id (the "onboarded"
 * marker), seed the session cache, and enter the app.
 */

import { useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useHistory } from 'react-router-dom';
import { useIntegrations, STORAGE_KEYS } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import { AppError } from '@/data/errors/app_error';
import { useOnboardingStore } from '@/state/stores/onboarding_store';
import type { Session } from '@/types/models';

export type AuthProvider = 'apple' | 'google';

export function useOnboarding() {
  const { auth, api, secureStore } = useIntegrations();
  const history = useHistory();
  const queryClient = useQueryClient();

  const selectedTrigger = useOnboardingStore((s) => s.selectedTrigger);
  const setSelectedTrigger = useOnboardingStore((s) => s.setSelectedTrigger);
  const step = useOnboardingStore((s) => s.step);
  const setStep = useOnboardingStore((s) => s.setStep);
  const reset = useOnboardingStore((s) => s.reset);

  const completion = useMutation<Session, unknown, AuthProvider>({
    mutationFn: async (provider) => {
      if (!selectedTrigger) {
        throw new AppError({
          code: 'unknown',
          userMessage: 'Pick what you want to feel quicker at first.',
          reason: 'missing_trigger',
        });
      }
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
      return api.completeOnboarding({
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        trigger: selectedTrigger,
        idToken,
      });
    },
    onSuccess: (session) => {
      void secureStore.set(STORAGE_KEYS.appUserId, session.appUserId);
      // Seed the session cache so the guards admit the app immediately.
      queryClient.setQueryData<Session>(queryKeys.session, session);
      reset();
      history.replace('/app/home');
    },
  });

  const selectTrigger = useCallback(
    (trigger: string) => {
      setSelectedTrigger(trigger);
      setStep('login');
    },
    [setSelectedTrigger, setStep],
  );

  const back = useCallback(() => setStep('trigger'), [setStep]);

  return {
    step,
    selectedTrigger,
    selectTrigger,
    back,
    signInWithApple: () => completion.mutateAsync('apple'),
    signInWithGoogle: () => completion.mutateAsync('google'),
    isCompleting: completion.isPending,
    completingProvider: completion.isPending
      ? (completion.variables ?? null)
      : null,
    error: completion.error,
  };
}
