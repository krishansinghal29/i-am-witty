/**
 * Recall tab view-model: what's left of today's session.
 *
 * The backend builds the day's session (focus check-ins + up to 15 cards) and
 * leaves out anything already seen today, so the same query doubles as
 * "what's left today". The session runner shares this query key, so the tab
 * and the session always agree.
 */

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { localDateString } from '@/lib/local_date';
import { queryKeys } from '@/state/query_keys';
import type { RecallCardKind } from '@/types/models';

export function useRecallToday() {
  const api = useRiffyApi();
  const localDate = localDateString();

  const query = useQuery({
    queryKey: queryKeys.recallSession(localDate),
    queryFn: () => api.getRecallSession(localDate),
  });
  const session = query.data ?? null;

  const summary = useMemo(() => {
    const cards = session?.cards ?? [];
    const kindCounts: Record<RecallCardKind, number> = { line: 0, concept: 0, routine: 0 };
    for (const card of cards) kindCounts[card.kind] += 1;
    const newCount = cards.filter((card) => card.isNew).length;
    const openCheckins = (session?.checkins ?? []).filter((c) => c.today === null);
    return {
      cardCount: cards.length,
      dueCount: cards.length - newCount,
      newCount,
      kindCounts,
      openCheckins,
    };
  }, [session]);

  return {
    ...summary,
    /** True when there is anything left to do today. */
    hasWork: summary.cardCount > 0 || summary.openCheckins.length > 0,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}
