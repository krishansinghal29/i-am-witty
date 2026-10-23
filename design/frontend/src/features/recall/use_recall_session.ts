/**
 * Recall session runner: steps through today's unanswered check-ins, then the
 * cards, one at a time (prompt → reveal → next).
 *
 * The plan is frozen from a fresh fetch when the session opens, so saving
 * progress mid-session never reshuffles what's on screen. Saves are
 * fire-and-forget (Next never waits on the network); failed ones are kept so
 * the user can retry. Finishing or leaving invalidates the recall queries so
 * the tab reflects the run.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  useIsMutating,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { useRiffyApi } from '@/app/providers';
import { recallDayString } from '@/lib/local_date';
import { queryKeys } from '@/state/query_keys';
import type {
  RecallCard,
  RecallCheckin,
  RecallCheckinResult,
  RecallSeenResult,
  RecallSession,
} from '@/types/models';

export type RecallStep =
  | { type: 'checkin'; checkin: RecallCheckin; number: number; total: number }
  | { type: 'card'; card: RecallCard; number: number; total: number };

type RecallWrite =
  | { type: 'seen'; itemId: string }
  | { type: 'checkin'; itemId: string; done: boolean };

const WRITE_KEY = ['recall', 'write'] as const;

/** Unanswered check-ins first, then every card, numbered within their group. */
export function buildRecallPlan(session: RecallSession): RecallStep[] {
  const checkins = session.checkins.filter((checkin) => checkin.today === null);
  return [
    ...checkins.map((checkin, i) => ({
      type: 'checkin' as const,
      checkin,
      number: i + 1,
      total: checkins.length,
    })),
    ...session.cards.map((card, i) => ({
      type: 'card' as const,
      card,
      number: i + 1,
      total: session.cards.length,
    })),
  ];
}

export function useRecallSession() {
  const api = useRiffyApi();
  const queryClient = useQueryClient();
  // Pinned for the whole run so a session that crosses midnight stays one day.
  const [localDate] = useState(() => recallDayString());

  const query = useQuery({
    queryKey: queryKeys.recallSession(localDate),
    queryFn: () => api.getRecallSession(localDate),
    // Always start from the server's latest (another device may have progressed).
    refetchOnMount: 'always',
  });

  const [plan, setPlan] = useState<RecallStep[] | null>(null);
  // Freeze the plan from the first settled fetch (state-from-render pattern).
  if (plan === null && query.data && !query.isFetching) {
    setPlan(buildRecallPlan(query.data));
  }

  const [index, setIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [answered, setAnswered] = useState({ checkins: 0, cards: 0 });
  const [failed, setFailed] = useState<RecallWrite[]>([]);

  const write = useMutation({
    mutationKey: WRITE_KEY,
    mutationFn: (w: RecallWrite): Promise<RecallSeenResult | RecallCheckinResult> =>
      w.type === 'seen'
        ? api.markRecallSeen(w.itemId, localDate)
        : api.recordRecallCheckin(w.itemId, localDate, w.done),
    // Options-level onError fires for every call, unlike per-mutate callbacks.
    onError: (_error, w) => setFailed((prev) => [...prev, w]),
  });
  const pendingWrites = useIsMutating({ mutationKey: WRITE_KEY });

  const step = plan?.[index] ?? null;
  const isDone = plan !== null && plan.length > 0 && index >= plan.length;
  const isEmpty = plan !== null && plan.length === 0;

  const advance = () => {
    setRevealed(false);
    setIndex((i) => i + 1);
  };

  const answerCheckin = (done: boolean) => {
    if (step?.type !== 'checkin') return;
    write.mutate({ type: 'checkin', itemId: step.checkin.itemId, done });
    setAnswered((a) => ({ ...a, checkins: a.checkins + 1 }));
    advance();
  };

  const next = () => {
    if (step?.type !== 'card') return;
    write.mutate({ type: 'seen', itemId: step.card.itemId });
    setAnswered((a) => ({ ...a, cards: a.cards + 1 }));
    advance();
  };

  const retryFailed = () => {
    const retry = failed;
    setFailed([]);
    retry.forEach((w) => write.mutate(w));
  };

  // Wait for the last saves to land so "due tomorrow" counts them.
  const outlook = useQuery({
    queryKey: queryKeys.recallOutlook(localDate),
    queryFn: () => api.getRecallOutlook(localDate),
    enabled: isDone && pendingWrites === 0,
    staleTime: 0,
  });

  // Once the run is finished and saved, refresh the tab's summary.
  const refreshedRef = useRef(false);
  useEffect(() => {
    if (!isDone || pendingWrites > 0 || refreshedRef.current) return;
    refreshedRef.current = true;
    void queryClient.invalidateQueries({ queryKey: queryKeys.recallSession(localDate) });
  }, [isDone, pendingWrites, queryClient, localDate]);

  /** Call when leaving the session (close / back) so every recall view refreshes. */
  const leave = useCallback(() => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.recall });
  }, [queryClient]);

  return {
    step,
    stepIndex: index,
    stepCount: plan?.length ?? 0,
    revealed,
    reveal: () => setRevealed(true),
    answerCheckin,
    next,
    isDone,
    isEmpty,
    answered,
    outlook: outlook.data ?? null,
    failedCount: failed.length,
    retryFailed,
    leave,
    isLoading: plan === null && !query.isError,
    isError: plan === null && query.isError,
    refetch: query.refetch,
  };
}
