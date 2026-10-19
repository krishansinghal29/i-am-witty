import type { Session } from '@/api/types';
import { Mark } from '@/components/Icons';
import { headerDate } from '@/lib/dates';

function plural(n: number, one: string, many: string) {
  return `${n} ${n === 1 ? one : many}`;
}

function streakLabel(streak: number, today: boolean | null) {
  if (today === true) return streak > 0 ? `Done · ${plural(streak, 'day', 'days')}` : 'Done';
  if (today === false) return 'Not today';
  return streak > 0 ? plural(streak, 'day', 'days') : 'New';
}

export function TodayScreen({ session, onStart }: { session: Session; onStart: () => void }) {
  const { cards, checkins, counts } = session;
  const pending = checkins.filter((c) => c.today === null).length;
  const nothingToDo = cards.length === 0 && pending === 0;

  const kinds = [
    { key: 'line', n: counts.line, label: plural(counts.line, 'line', 'lines') },
    { key: 'concept', n: counts.concept, label: plural(counts.concept, 'concept', 'concepts') },
    { key: 'routine', n: counts.routine, label: plural(counts.routine, 'routine', 'routines') },
  ].filter((k) => k.n > 0);

  return (
    <div className="screen">
      <header className="appbar">
        <span className="logo">
          <Mark />
          Recall
        </span>
        <span className="date">{headerDate()}</span>
      </header>
      <main className="body">
        <div>
          <h1 className="h-xl">Today's recall</h1>
          <p className="sub">Say each one out loud before you reveal it.</p>
        </div>

        {nothingToDo ? (
          <div className="card empty">
            <b>Nothing due today.</b>
            <p className="sub">Come back tomorrow.</p>
          </div>
        ) : cards.length > 0 ? (
          <div className="card">
            <div className="big">
              <span className="num">{cards.length}</span>
              <span className="unit">{cards.length === 1 ? 'card' : 'cards'}</span>
            </div>
            <div className="split">
              <span>
                <b>{counts.due}</b> due
              </span>
              <span>
                <b>{counts.new}</b> new
              </span>
            </div>
            {kinds.length > 0 && (
              <div className="chiprow">
                {kinds.map((k) => (
                  <span key={k.key} className={`chip k-${k.key}`}>
                    {k.label}
                  </span>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="card">
            <p className="sub">No cards due today. Just your check-ins.</p>
          </div>
        )}

        {checkins.length > 0 && (
          <>
            <div className="list-h">{pending > 0 ? 'Check-ins first' : 'Check-ins'}</div>
            <div className="card">
              {checkins.map((c) => (
                <div className="mrow" key={c.item_id}>
                  <span className="chip k-focus">Focus</span>
                  <b>{c.title}</b>
                  <span className="streak">{streakLabel(c.streak, c.today)}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </main>
      {!nothingToDo && (
        <footer className="foot">
          <button type="button" className="btn warm" onClick={onStart}>
            Start
          </button>
        </footer>
      )}
    </div>
  );
}
