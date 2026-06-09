/**
 * Onboarding-state hook.
 *
 * Depends on a session existing (it needs the guest/auth token), so the query is
 * gated on `useSession()` resolving before it fires.
 */

import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { queryKeys } from '@/state/query_keys';
import { useSession } from '@/features/identity/use_session';

export function useOnboardingState() {
  const api = useRiffyApi();
  const { session } = useSession();

  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.onboarding,
    queryFn: () => api.getOnboarding(),
    enabled: !!session,
  });

  return {
    onboarding: data ?? null,
    isLoading,
    isError,
    isComplete: !!data?.completedAt,
  };
}
