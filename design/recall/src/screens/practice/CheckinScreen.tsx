import type { Checkin } from '@/api/types';
import { CheckIcon, CloseIcon } from '@/components/Icons';
import { weekdayLetter } from '@/lib/dates';

interface Props {
  checkin: Checkin;
  localDate: string;
  index: number;
  total: number;
  busy: boolean;
  onAnswer: (done: boolean) => void;
  onClose: () => void;
}

export function CheckinScreen({ checkin, localDate, index, total, busy, onAnswer, onClose }: Props) {
  const percent = Math.round(((index + 1) / total) * 100);

  return (
    <div className="screen">
      <header className="appbar">
        <button type="button" className="iconbtn" aria-label="Close" onClick={onClose}>
          <CloseIcon />
        </button>
        <div className="prog" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={index + 1}>
          <i style={{ width: `${percent}%` }} />
        </div>
        <span className="count">
          Check-in {index + 1} of {total}
        </span>
      </header>
      <main className="body">
        <div className="card">
          <span className="chip k-focus">Focus check-in</span>
          <h1 className="cue">{checkin.title}</h1>
          <p className="question">{checkin.question}</p>
          {checkin.why && (
            <div className="note">
              <b>Why</b>
              {checkin.why}
            </div>
          )}
          <div className="week" aria-label="Last 7 days">
            {checkin.last7.map((day) => {
              const isToday = day.date === localDate;
              const cls = day.done ? 'ok' : isToday ? 'now' : '';
              return (
                <div key={day.date}>
                  <i className={cls}>{day.done && <CheckIcon />}</i>
                  {weekdayLetter(day.date)}
                </div>
              );
            })}
          </div>
          <span className="streak">
            {checkin.streak > 0 ? `${checkin.streak}-day streak` : 'Start your streak today'}
          </span>
        </div>
      </main>
      <footer className="foot">
        <button type="button" className="btn ghost" disabled={busy} onClick={() => onAnswer(false)}>
          No
        </button>
        <button type="button" className="btn cool" disabled={busy} onClick={() => onAnswer(true)}>
          Yes
        </button>
      </footer>
    </div>
  );
}
