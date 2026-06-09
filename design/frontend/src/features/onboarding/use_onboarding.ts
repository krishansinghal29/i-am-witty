/**
 * Onboarding view-model.
 *
 * Resolves the current UX step from three signals (least to most authoritative
 * never below a "floor"):
 *   - the locally reached step held in `onboarding_store` (drives the late steps
 *     the backend does not advance: variable_reward -> login -> reminder ->
 *     plan_landing),
 *   - the backend onboarding step (drives trigger -> tiny_practice and, when it
 *     advances, first_win),
 *   - a progress-derived "first win" signal from `/v1/home`, so the user resumes
 *     at the celebration even if the backend step hasn't advanced.
 *
 * Invalidations follow the backend's bundled transactions: saving the trigger
 * invalidates `onboarding` + `home` (the backend assigns the first task).
 */

import { useCallback, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useHistory } from 'react-router-dom';
import { useWittyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import { useSession } from '@/features/identity/use_session';
import { useOnboardingStore } from '@/state/stores/onboarding_store';
import type { OnboardingState } from '@/types/models';
import {
  BACKEND_ADVANCE_TARGET,
  PROGRESS_SEGMENTS,
  UX_STEPS,
  hasFirstWin,
  nextUxStep,
  progressFilled,
  uxStepForState,
  uxStepIndex,
} from './onboarding_machine';
import type { UxStep } from './onboarding_machine';

export interface UseOnboarding {
  /** The UX step to render right now. */
  step: UxStep;
  onboarding: OnboardingState | null;
  selectedTrigger: string | null;
  firstTaskId: string | null;
  isLoading: boolean;
  isError: boolean;
  isSavingTrigger: boolean;
  triggerError: unknown;
  /** Progress-bar fill state for the chrome. */
  progress: { filled: number; total: number };
  canGoBack: boolean;
  /** Persist the chosen trigger; the backend assigns the first task. */
  selectTrigger: (trigger: string) => Promise<unknown>;
  /** Open the first-task runtime (text-first, calm) at `?source=onboarding`. */
  startFirstTask: () => void;
  /** Move one step forward (client-driven late steps). */
  advance: () => void;
  /** Move one step back, never behind the server-established floor. */
  back: () => void;
  /** Re-read onboarding + home (used on view-enter to pick up the first win). */
  refresh: () => void;
  /** Finish onboarding and enter the app. */
  completeAndEnter: () => void;
}

export function useOnboarding(): UseOnboarding {
  const api = useWittyApi();
  const history = useHistory();
  const queryClient = useQueryClient();
  const { session } = useSession();

  const selectedTrigger = useOnboardingStore((s) => s.selectedTrigger);
  const setSelectedTrigger = useOnboardingStore((s) => s.setSelectedTrigger);
  const storedStep = useOnboardingStore((s) => s.uxStep);
  const setUxStep = useOnboardingStore((s) => s.setUxStep);
  const resetStore = useOnboardingStore((s) => s.reset);

  const onboardingQuery = useQuery({
    queryKey: queryKeys.onboarding,
    queryFn: () => api.getOnboarding(),
    enabled: !!session,
  });
  const onboarding = onboardingQuery.data ?? null;

  // Read only to detect the "first win": the backend bundles progress into
  // `/v1/home`, and completing the first task increments completedTaskCount.
  const homeQuery = useQuery({
    queryKey: queryKeys.home,
    queryFn: () => api.getHome(),
    enabled: !!session,
  });
  const firstWin =
    hasFirstWin(onboarding) ||
    (homeQuery.data?.progress.completedTaskCount ?? 0) > 0;

  // Floor: the earliest step the user is allowed to be at, given server truth.
  let floorIndex = uxStepIndex(uxStepForState(onboarding));
  if (firstWin) {
    floorIndex = Math.max(floorIndex, uxStepIndex('variable_reward'));
  }

  const step = UX_STEPS[Math.max(uxStepIndex(storedStep), floorIndex)];

  // Keep the store monotonically in sync with the floor (never moves backward).
  useEffect(() => {
    if (uxStepIndex(storedStep) < floorIndex) {
      setUxStep(UX_STEPS[floorIndex]);
    }
  }, [storedStep, floorIndex, setUxStep]);

  const triggerMutation = useMutation({
    mutationFn: (trigger: string) => api.saveTrigger(trigger),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.onboarding }),
        queryClient.invalidateQueries({ queryKey: queryKeys.home }),
      ]);
      setUxStep('tiny_practice');
    },
  });

  // Backend step advancement for the late steps. Each transition sets the
  // server step to match the step the user is now on, so resume is authoritative
  // (the client store is just optimistic UI on top).
  const advanceMutation = useMutation({
    mutationFn: (target: string) => api.advanceOnboarding(target),
    onSuccess: (state) => {
      queryClient.setQueryData<OnboardingState>(queryKeys.onboarding, state);
      void queryClient.invalidateQueries({ queryKey: queryKeys.home });
    },
  });

  const selectTrigger = useCallback(
    (trigger: string) => {
      setSelectedTrigger(trigger);
      return triggerMutation.mutateAsync(trigger);
    },
    [setSelectedTrigger, triggerMutation],
  );

  const startFirstTask = useCallback(() => {
    const taskId = onboarding?.firstTaskId;
    if (!taskId) return;
    history.push(`/task/${taskId}?source=onboarding`);
  }, [history, onboarding?.firstTaskId]);

  const advance = useCallback(() => {
    // Optimistically move the UI forward, then persist the matching backend
    // step where one exists (plan_landing has no backend step — `complete` is
    // stamped by `completeAndEnter`).
    setUxStep(nextUxStep(step));
    const target = BACKEND_ADVANCE_TARGET[step];
    if (target) advanceMutation.mutate(target);
  }, [advanceMutation, setUxStep, step]);

  const back = useCallback(() => {
    const target = Math.max(uxStepIndex(step) - 1, floorIndex);
    setUxStep(UX_STEPS[target]);
  }, [floorIndex, setUxStep, step]);

  const refresh = useCallback(() => {
    void onboardingQuery.refetch();
    void homeQuery.refetch();
  }, [onboardingQuery, homeQuery]);

  const completeAndEnter = useCallback(async () => {
    // Stamp `completed_at` server-side so `OnboardingGuard` admits `/app`.
    try {
      const state = await api.advanceOnboarding('complete');
      queryClient.setQueryData<OnboardingState>(queryKeys.onboarding, state);
    } catch {
      // Never trap the user: fall back to an optimistic complete in cache; a
      // later server refetch with a real `completed_at` yields the same result.
      queryClient.setQueryData<OnboardingState>(queryKeys.onboarding, (prev) => ({
        currentStep: 'complete',
        selectedTrigger: prev?.selectedTrigger ?? selectedTrigger,
        firstTaskId: prev?.firstTaskId ?? null,
        firstTaskAttemptId: prev?.firstTaskAttemptId ?? null,
        completedAt: new Date().toISOString(),
      }));
    }
    void queryClient.invalidateQueries({ queryKey: queryKeys.home });
    resetStore();
    history.replace('/app/home');
  }, [api, history, queryClient, resetStore, selectedTrigger]);

  return {
    step,
    onboarding,
    selectedTrigger,
    firstTaskId: onboarding?.firstTaskId ?? null,
    isLoading: onboardingQuery.isLoading,
    isError: onboardingQuery.isError,
    isSavingTrigger: triggerMutation.isPending,
    triggerError: triggerMutation.error,
    progress: { filled: progressFilled(step), total: PROGRESS_SEGMENTS },
    canGoBack: uxStepIndex(step) > floorIndex,
    selectTrigger,
    startFirstTask,
    advance,
    back,
    refresh,
    completeAndEnter,
  };
}
