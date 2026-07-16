/**
 * Advances a multi-turn (roleplay) attempt by one turn.
 *
 * Each call posts the user's latest line to `/v1/attempts/:id/turn` and returns
 * the next AI line + progress. The goal-reaching turn finalizes the attempt
 * server-side (streak/usage), so on completion we invalidate the surfaces the
 * backend wrote — `home` + `access` — mirroring {@link useTaskAttempt}.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type { TurnTaskResult } from '@/types/models';

export interface AttemptTurnController {
  turn: (body: { clientTranscript?: string }) => Promise<TurnTaskResult>;
  isSubmitting: boolean;
  isError: boolean;
}

export function useAttemptTurn(attemptId: string | null): AttemptTurnController {
  const api = useRiffyApi();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (body: { clientTranscript?: string }) => {
      if (!attemptId) {
        throw new Error('Cannot advance: no active attempt');
      }
      return api.turnAttempt(attemptId, body);
    },
    onSuccess: (data: TurnTaskResult) => {
      // Each turn consumes one attempt, so keep the access (remaining count)
      // fresh after every turn. Home and streak only change on session completion.
      void queryClient.invalidateQueries({ queryKey: queryKeys.access });
      if (data.turn.isComplete) {
        void queryClient.invalidateQueries({ queryKey: queryKeys.home });
      }
    },
  });

  return {
    turn: (body) => mutation.mutateAsync(body),
    isSubmitting: mutation.isPending,
    isError: mutation.isError,
  };
}
