/**
 * Onboarding view-model (login-only, client-side until completion).
 *
 * Two steps held in `onboarding_store`: pick a trigger (no network), then sign
 * in. Signing in is the single write of the whole flow: it authenticates with
 * Firebase (Apple, Google, or email/password), then
 * `POST /v1/onboarding/complete` creates the user + onboarding row and returns
 * the session. We persist the backend id (the "onboarded" marker), seed the
 * session cache, and enter the app.
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

/**
 * Which auth control drives the single onboarding-completion write. The Firebase
 * step varies (OAuth popup/plugin vs email+password); the tail — verify token,
 * create user, enter app — is shared.
 */
export type AuthAction =
  | { kind: 'apple' }
  | { kind: 'google' }
  | { kind: 'email-signup'; email: string; password: string }
  | { kind: 'email-login'; email: string; password: string };

export type AuthActionKind = AuthAction['kind'];

export type PasswordResetState = 'idle' | 'sending' | 'sent' | 'error';

export function useOnboarding() {
  const { auth, api, secureStore } = useIntegrations();
  const history = useHistory();
  const queryClient = useQueryClient();

  const selectedTrigger = useOnboardingStore((s) => s.selectedTrigger);
  const setSelectedTrigger = useOnboardingStore((s) => s.setSelectedTrigger);
  const step = useOnboardingStore((s) => s.step);
  const setStep = useOnboardingStore((s) => s.setStep);
  const reset = useOnboardingStore((s) => s.reset);

  const completion = useMutation<Session, unknown, AuthAction>({
    mutationFn: async (action) => {
      if (!selectedTrigger) {
        throw new AppError({
          code: 'unknown',
          userMessage: 'Pick what you want to feel quicker at first.',
          reason: 'missing_trigger',
        });
      }
      // Authenticate with Firebase via the chosen method.
      switch (action.kind) {
        case 'apple':
          await auth.signInWithApple();
          break;
        case 'google':
          await auth.signInWithGoogle();
          break;
        case 'email-signup':
          await auth.signUpWithEmail(action.email, action.password);
          break;
        case 'email-login':
          await auth.signInWithEmail(action.email, action.password);
          break;
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

  // Forgot-password is independent of completion: it sends a reset email and
  // never enters the app.
  const passwordReset = useMutation<void, unknown, string>({
    mutationFn: (email) => auth.sendPasswordReset(email),
  });

  const selectTrigger = useCallback(
    (trigger: string) => {
      setSelectedTrigger(trigger);
      setStep('login');
    },
    [setSelectedTrigger, setStep],
  );

  const back = useCallback(() => setStep('trigger'), [setStep]);

  const activeAction: AuthActionKind | null = completion.isPending
    ? (completion.variables?.kind ?? null)
    : null;

  const forgotPasswordState: PasswordResetState = passwordReset.isPending
    ? 'sending'
    : passwordReset.isError
      ? 'error'
      : passwordReset.isSuccess
        ? 'sent'
        : 'idle';

  return {
    step,
    selectedTrigger,
    selectTrigger,
    back,
    signInWithApple: () => completion.mutateAsync({ kind: 'apple' }),
    signInWithGoogle: () => completion.mutateAsync({ kind: 'google' }),
    signUpWithEmail: (email: string, password: string) =>
      completion.mutateAsync({ kind: 'email-signup', email, password }),
    logInWithEmail: (email: string, password: string) =>
      completion.mutateAsync({ kind: 'email-login', email, password }),
    forgotPassword: (email: string) => passwordReset.mutateAsync(email),
    isCompleting: completion.isPending,
    activeAction,
    error: completion.error,
    forgotPasswordState,
    forgotPasswordError: passwordReset.error,
  };
}
