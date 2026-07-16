/**
 * The {@link AttemptController} for a runtime view: a single `completeTask`
 * mutation plus its lifecycle status.
 *
 * On success it invalidates the surfaces the backend wrote inside the same
 * transaction. The backend bundles plan + progress + access into `/v1/home`
 * and returns the free-limit inline in the completion response, so the
 * invalidation set is `home` + `access` only.
 */

import { useEffect, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { useFreeLimit } from '@/features/entitlement/use_free_limit';
import { queryKeys } from '@/state/query_keys';
import type {
  AttemptController,
  AttemptStatus,
  VoiceCompleteBody,
} from '@/components/task_runtime/contract';

export function useTaskAttempt(
  attemptId: string | null,
): AttemptController<VoiceCompleteBody> {
  const api = useRiffyApi();
  const queryClient = useQueryClient();
  const { handlePaywallRequired } = useFreeLimit();
  const [paywallOnDone, setPaywallOnDone] = useState(false);

  useEffect(() => {
    setPaywallOnDone(false);
  }, [attemptId]);

  const mutation = useMutation({
    mutationFn: (body: VoiceCompleteBody) => {
      if (!attemptId) {
        throw new Error('Cannot complete: no active attempt');
      }
      return api.completeTask(attemptId, body);
    },
    onSuccess: (data) => {
      if (data.freeLimit.shouldPaywall) {
        setPaywallOnDone(true);
      }
      void queryClient.invalidateQueries({ queryKey: queryKeys.home });
      void queryClient.invalidateQueries({ queryKey: queryKeys.access });
    },
    onError: (error) => {
      handlePaywallRequired(error);
    },
  });

  const status: AttemptStatus = mutation.isPending
    ? 'submitting'
    : mutation.isError
      ? 'error'
      : mutation.isSuccess
        ? 'success'
        : 'idle';

  return {
    complete: (body: VoiceCompleteBody) => mutation.mutateAsync(body),
    isSubmitting: mutation.isPending,
    result: mutation.data ?? null,
    status,
    paywallOnDone,
  };
}
