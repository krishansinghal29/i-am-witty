/**
 * Generates the next rep's scenario for a multi-rep (single-shot) attempt.
 *
 * Backs the "Next" button: each call posts to `/v1/attempts/:id/next-round` and
 * returns a fresh prompt + the unchanged rep counter. It never finalizes the
 * attempt (completion happens on the final `complete`), so — unlike
 * {@link useTaskAttempt} — there is nothing to invalidate here.
 */

import { useMutation } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import type { NextRoundResult } from '@/types/models';

export interface AttemptNextRoundController {
  nextRound: () => Promise<NextRoundResult>;
  isSubmitting: boolean;
  isError: boolean;
}

export function useAttemptNextRound(
  attemptId: string | null,
): AttemptNextRoundController {
  const api = useRiffyApi();

  const mutation = useMutation({
    mutationFn: () => {
      if (!attemptId) {
        throw new Error('Cannot advance: no active attempt');
      }
      return api.nextRound(attemptId);
    },
  });

  return {
    nextRound: () => mutation.mutateAsync(),
    isSubmitting: mutation.isPending,
    isError: mutation.isError,
  };
}
