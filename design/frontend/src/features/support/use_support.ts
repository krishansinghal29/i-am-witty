/**
 * Support-message view-model.
 *
 * A fire-and-forget mutation over `POST /v1/support-messages` (no query key —
 * support submissions are not cached or read back). Exposes the calm states the
 * support sheet needs: `submit`, `isSubmitting`, `isSuccess`, `error`, `reset`.
 */

import { useMutation } from '@tanstack/react-query';
import { useWittyApi } from '@/app/providers';
import type { SupportMessage } from '@/types/models';

export interface SubmitSupportInput {
  messageText: string;
  sourceScreen?: string | null;
}

export function useSupport() {
  const api = useWittyApi();

  const mutation = useMutation<SupportMessage, unknown, SubmitSupportInput>({
    mutationFn: (input) => api.submitSupport(input),
  });

  return {
    submit: (input: SubmitSupportInput) => mutation.mutateAsync(input),
    isSubmitting: mutation.isPending,
    isSuccess: mutation.isSuccess,
    error: mutation.error,
    reset: mutation.reset,
  };
}
