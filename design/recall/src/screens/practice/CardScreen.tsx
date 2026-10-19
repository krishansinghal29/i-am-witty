import { useEffect } from 'react';
import type { Card } from '@/api/types';
import { CloseIcon } from '@/components/Icons';

interface Props {
  card: Card;
  index: number;
  total: number;
  revealed: boolean;
  onReveal: () => void;
  onNext: () => void;
  onClose: () => void;
}

const KIND_LABEL = { line: 'Line', concept: 'Concept', routine: 'Routine' } as const;

const SAY_IT = {
  line: 'Say your line out loud, then reveal.',
  concept: 'Name the concept out loud, then reveal.',
  routine: 'Say the steps in order, then reveal.',
} as const;

function quote(text: string) {
  return `“${text}”`;
}

function Prompt({ card }: { card: Card }) {
  switch (card.kind) {
    case 'line': {
      const { line } = card;
      return (
        <>
          <span className="eyebrow">{line.cue_type === 'reaction' ? 'She says' : 'Goal'}</span>
          <h1 className="cue">{line.cue_type === 'reaction' ? quote(line.cue_text) : line.cue_text}</h1>
          {line.hint && (
            <div className="hintrow">
              <span>Answer with</span>
              <span className="hint">{line.hint}</span>
            </div>
          )}
        </>
      );
    }
    case 'concept':
      return (
        <>
          <span className="eyebrow">Which concept is this?</span>
          <p className="scenario">{card.concept.scenario}</p>
        </>
      );
    case 'routine':
      return (
        <>
          <span className="eyebrow">Recall the steps</span>
          <h1 className="cue">{card.routine.name}</h1>
        </>
      );
  }
}

function Answer({ card }: { card: Card }) {
  switch (card.kind) {
    case 'line': {
      const { line } = card;
      return (
        <>
          <span className="eyebrow">Your line</span>
          <p className="answer">{quote(line.text)}</p>
          {line.delivery_note && (
            <div className="note">
              <b>How to say it</b>
              {line.delivery_note}
            </div>
          )}
          {line.cue_line_count > 1 && (
            <span className="meta">
              {line.position} of {line.cue_line_count} lines on this cue
            </span>
          )}
        </>
      );
    }
    case 'concept': {
      const { concept } = card;
      return (
        <>
          <span className="eyebrow">Concept</span>
          <p className="answer">{concept.name}</p>
          <p className="sub">{concept.definition}</p>
          {concept.scenario_count > 1 && (
            <span className="meta">
              Scenario {concept.scenario_number} of {concept.scenario_count}
            </span>
          )}
        </>
      );
    }
    case 'routine':
      return (
        <ol className="steps">
          {card.routine.steps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      );
  }
}

export function CardScreen({ card, index, total, revealed, onReveal, onNext, onClose }: Props) {
  const percent = Math.round(((index + 1) / total) * 100);
  const isLast = index + 1 === total;

  // Enter or Space runs the main button, unless focus is on another control.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      const target = event.target as HTMLElement | null;
      if (target && target.closest('button, a, input, textarea')) return;
      event.preventDefault();
      if (revealed) onNext();
      else onReveal();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [revealed, onNext, onReveal]);

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
          {index + 1} / {total}
        </span>
      </header>
      <main className="body">
        <div className="card">
          <div className="chiprow">
            <span className={`chip k-${card.kind}`}>{KIND_LABEL[card.kind]}</span>
            {card.is_new && <span className="chip k-muted">New</span>}
          </div>
          <Prompt card={card} />
          {revealed && (
            <div className="reveal">
              <Answer card={card} />
            </div>
          )}
        </div>
        {!revealed && <p className="say">{SAY_IT[card.kind]}</p>}
      </main>
      <footer className="foot">
        {revealed ? (
          <button type="button" className="btn warm" onClick={onNext}>
            {isLast ? 'Finish' : 'Next'}
          </button>
        ) : (
          <button type="button" className="btn cool" onClick={onReveal}>
            Reveal
          </button>
        )}
      </footer>
    </div>
  );
}
