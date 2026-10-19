/**
 * Public practice: Today -> check-ins -> cards -> Done, as one state machine on
 * "/". Reloading resumes naturally because the server leaves out anything
 * already seen or answered today.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { answerCheckin, getSession, markSeen } from '@/api/recall';
import { errorMessage } from '@/api/http';
import type { Card, Checkin, Session } from '@/api/types';
import { useToast } from '@/components/Toast';
import { localDate } from '@/lib/dates';
import { CardScreen } from './CardScreen';
import { CheckinScreen } from './CheckinScreen';
import { DoneScreen } from './DoneScreen';
import { TodayScreen } from './TodayScreen';

type Phase =
  | { name: 'loading' }
  | { name: 'error'; message: string }
  | { name: 'today' }
  | { name: 'checkin'; index: number }
  | { name: 'card'; index: number; revealed: boolean }
  | { name: 'done' };

interface Queue {
  checkins: Checkin[];
  cards: Card[];
}

export function PracticePage() {
  const toast = useToast();
  const [session, setSession] = useState<Session | null>(null);
  const [phase, setPhase] = useState<Phase>({ name: 'loading' });
  const [queue, setQueue] = useState<Queue>({ checkins: [], cards: [] });
  const [stats, setStats] = useState({ cards: 0, checkins: 0 });
  const [answering, setAnswering] = useState(false);
  const pendingSeen = useRef(new Set<Promise<unknown>>());
  const sessionDate = useRef(localDate());

  const waitForSeen = useCallback(async () => {
    await Promise.allSettled([...pendingSeen.current]);
  }, []);

  const load = useCallback(async () => {
    setPhase({ name: 'loading' });
    await waitForSeen();
    const date = localDate();
    sessionDate.current = date;
    try {
      const next = await getSession(date);
      setSession(next);
      setPhase({ name: 'today' });
    } catch (error) {
      setPhase({ name: 'error', message: errorMessage(error) });
    }
  }, [waitForSeen]);

  useEffect(() => {
    void load();
  }, [load]);

  const start = () => {
    if (!session) return;
    const next: Queue = {
      checkins: session.checkins.filter((c) => c.today === null),
      cards: session.cards,
    };
    setQueue(next);
    setStats({ cards: 0, checkins: 0 });
    if (next.checkins.length > 0) setPhase({ name: 'checkin', index: 0 });
    else if (next.cards.length > 0) setPhase({ name: 'card', index: 0, revealed: false });
    else setPhase({ name: 'done' });
  };

  const afterCheckins = () => {
    if (queue.cards.length > 0) setPhase({ name: 'card', index: 0, revealed: false });
    else setPhase({ name: 'done' });
  };

  const answer = async (index: number, done: boolean) => {
    const checkin = queue.checkins[index];
    setAnswering(true);
    try {
      const result = await answerCheckin(checkin.item_id, sessionDate.current, done);
      setSession((s) =>
        s && {
          ...s,
          checkins: s.checkins.map((c) =>
            c.item_id === checkin.item_id ? { ...c, today: result.done, streak: result.streak } : c,
          ),
        },
      );
      setStats((s) => ({ ...s, checkins: s.checkins + 1 }));
      if (index + 1 < queue.checkins.length) setPhase({ name: 'checkin', index: index + 1 });
      else afterCheckins();
    } catch (error) {
      toast(errorMessage(error), { tone: 'error' });
    } finally {
      setAnswering(false);
    }
  };

  const recordSeen = useCallback(
    (itemId: string, date: string) => {
      const attempt = markSeen(itemId, date)
        .catch(() => {
          toast("Couldn't save progress for that card.", {
            tone: 'error',
            actionLabel: 'Retry',
            onAction: () => recordSeen(itemId, date),
          });
        })
        .finally(() => pendingSeen.current.delete(attempt));
      pendingSeen.current.add(attempt);
    },
    [toast],
  );

  const next = (index: number) => {
    recordSeen(queue.cards[index].item_id, sessionDate.current);
    setStats((s) => ({ ...s, cards: s.cards + 1 }));
    if (index + 1 < queue.cards.length) setPhase({ name: 'card', index: index + 1, revealed: false });
    else setPhase({ name: 'done' });
  };

  switch (phase.name) {
    case 'loading':
      return (
        <div className="screen">
          <div className="loading" aria-label="Loading">
            <div className="spinner" />
          </div>
        </div>
      );
    case 'error':
      return (
        <div className="screen">
          <div className="body" style={{ justifyContent: 'center' }}>
            <div className="banner error" role="alert">
              <span>{phase.message}</span>
            </div>
            <button type="button" className="btn ghost" style={{ flex: 'none' }} onClick={() => void load()}>
              Try again
            </button>
          </div>
        </div>
      );
    case 'today':
      return session ? <TodayScreen session={session} onStart={start} /> : null;
    case 'checkin':
      return (
        <CheckinScreen
          key={queue.checkins[phase.index].item_id}
          checkin={queue.checkins[phase.index]}
          localDate={sessionDate.current}
          index={phase.index}
          total={queue.checkins.length}
          busy={answering}
          onAnswer={(done) => void answer(phase.index, done)}
          onClose={() => void load()}
        />
      );
    case 'card':
      return (
        <CardScreen
          key={queue.cards[phase.index].item_id}
          card={queue.cards[phase.index]}
          index={phase.index}
          total={queue.cards.length}
          revealed={phase.revealed}
          onReveal={() => setPhase({ ...phase, revealed: true })}
          onNext={() => next(phase.index)}
          onClose={() => void load()}
        />
      );
    case 'done':
      return (
        <DoneScreen
          cards={stats.cards}
          checkins={stats.checkins}
          localDate={sessionDate.current}
          waitForSeen={waitForSeen}
          onRestart={() => void load()}
        />
      );
  }
}
