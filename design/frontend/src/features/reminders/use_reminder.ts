/**
 * Reminder preference (read via `GET /v1/reminders`, write via `PUT`).
 *
 * Flow: the user picks a timing/time, THEN (native only) we request the OS
 * notification permission, THEN we persist the preference. On web the permission
 * call is a no-op (`unsupported`) and is never blocking — web push is out of
 * scope, but the preference still persists server-side. On save we invalidate
 * `reminder` and `onboarding` (it may advance the flow).
 */

import { useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useIntegrations } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import { useSession } from '@/features/identity/use_session';
import type { Reminder } from '@/types/models';

/** Backend `ReminderStatus` values (enabled | skipped | disabled). */
export type SaveReminderStatus = 'enabled' | 'skipped' | 'disabled';

export interface SaveReminderInput {
  status: SaveReminderStatus;
  /** Relative timing slot, e.g. `before_work` (mutually exclusive with time). */
  timingKey?: string | null;
  /** Fixed local time as `HH:MM`, e.g. `20:00`. */
  localTime?: string | null;
}

export interface UseReminder {
  reminder: Reminder | null;
  isLoading: boolean;
  isError: boolean;
  save: (input: SaveReminderInput) => Promise<Reminder>;
  /** Persist a "skipped" preference (no nudge) and resolve. */
  skip: () => Promise<Reminder>;
  isSaving: boolean;
  error: unknown;
}

function deviceTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

export function useReminder(): UseReminder {
  const { api, device } = useIntegrations();
  const queryClient = useQueryClient();
  const { session } = useSession();

  const query = useQuery({
    queryKey: queryKeys.reminder,
    queryFn: () => api.getReminder(),
    enabled: !!session,
  });

  const mutation = useMutation<Reminder, unknown, SaveReminderInput>({
    mutationFn: async (input) => {
      // Ask for OS permission only when actually enabling a nudge; native-only,
      // best-effort, never blocks the save (web returns 'unsupported').
      if (input.status === 'enabled') {
        try {
          await device.requestNotificationPermission();
        } catch {
          // Permission denial/unavailability must not block saving the pref.
        }
      }
      return api.saveReminder({
        status: input.status,
        timingKey: input.timingKey ?? null,
        localTime: input.localTime ?? null,
        timezone: deviceTimezone(),
      });
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.reminder }),
        queryClient.invalidateQueries({ queryKey: queryKeys.onboarding }),
      ]);
    },
  });

  const save = useCallback(
    (input: SaveReminderInput) => mutation.mutateAsync(input),
    [mutation],
  );

  const skip = useCallback(
    () => mutation.mutateAsync({ status: 'skipped' }),
    [mutation],
  );

  return {
    reminder: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    save,
    skip,
    isSaving: mutation.isPending,
    error: mutation.error,
  };
}
