import { useEffect, useState } from 'react';
import { getOutlook } from '@/api/recall';
import type { Outlook } from '@/api/types';
import { Mark } from '@/components/Icons';

interface Props {
  cards: number;
  checkins: number;
  localDate: string;
  waitForSeen: () => Promise<void>;
  onRestart: () => void;
}

function summary(cards: number, checkins: number) {
  const parts: string[] = [];
  if (cards > 0) parts.push(`${cards} ${cards === 1 ? 'card' : 'cards'}`);
  if (checkins > 0) parts.push(`${checkins} ${checkins === 1 ? 'check-in' : 'check-ins'}`);
  return parts.length > 0 ? `${parts.join(' and ')}.` : 'Nothing left for today.';
}

export function DoneScreen({ cards, checkins, localDate, waitForSeen, onRestart }: Props) {
  const [outlook, setOutlook] = useState<Outlook | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      // Make sure every "seen" write has landed before asking what's due next.
      await waitForSeen();
      try {
        const result = await getOutlook(localDate);
        if (!cancelled) setOutlook(result);
      } catch {
        if (!cancelled) setFailed(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [localDate, waitForSeen]);

  return (
    <div className="screen">
      <main className="body">
        <div className="done-hero">
          <div className="done-ring">
            <Mark size={52} />
          </div>
          <h1 className="h-xl center">Done for today</h1>
          <p className="sub center">{summary(cards, checkins)}</p>
        </div>
        <div className="card">
          <div className="kv">
            <span>Next session</span>
            <b>Tomorrow</b>
          </div>
          <div className="kv">
            <span>Due tomorrow</span>
            <b>{outlook ? `${outlook.due_tomorrow} ${outlook.due_tomorrow === 1 ? 'card' : 'cards'}` : failed ? '–' : '…'}</b>
          </div>
          <div className="kv">
            <span>New items waiting</span>
            <b>{outlook ? outlook.new_waiting : failed ? '–' : '…'}</b>
          </div>
        </div>
      </main>
      <footer className="foot">
        <button type="button" className="btn ghost" onClick={onRestart}>
          Back to start
        </button>
      </footer>
    </div>
  );
}
