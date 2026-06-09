/**
 * Fetches (and resumes) the runtime payload for a task.
 *
 * `getTaskRuntime` is a POST that creates or resumes the server-side attempt,
 * so this query is configured to never silently re-fire (no window-focus /
 * reconnect refetch, effectively infinite stale time). The `source` and
 * `dailyPlanItemId` are read from the route query string when present.
 */

import { useQuery } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import type { TaskRuntime } from '@/types/models';

export interface UseTaskRuntimeResult {
  data: TaskRuntime | undefined;
  isLoading: boolean;
  isError: boolean;
  refetch: () => void;
}

export function useTaskRuntime(taskId: string | undefined): UseTaskRuntimeResult {
  const api = useRiffyApi();
  const location = useLocation();

  const params = new URLSearchParams(location.search);
  const source = params.get('source') ?? 'practice_library';
  const dailyPlanItemId =
    params.get('dailyPlanItemId') ?? params.get('daily_plan_item_id') ?? undefined;

  const query = useQuery({
    queryKey: queryKeys.taskRuntime(taskId ?? 'unknown'),
    queryFn: () =>
      api.getTaskRuntime(taskId as string, {
        source,
        ...(dailyPlanItemId != null ? { dailyPlanItemId } : {}),
      }),
    enabled: Boolean(taskId),
    staleTime: Infinity,
    gcTime: 0,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: false,
  });

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: () => {
      void query.refetch();
    },
  };
}
