import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { checkmark } from 'ionicons/icons';
import { Card, RiffyMark } from '@/components/ui';
import { colors } from '@/theme/tokens';
import type { RecallCard, RecallCheckin, RecallOutlook } from '@/types/models';
import {
  ANSWER,
  BODY_TEXT,
  CARD_STACK,
  CHIP_ROW,
  CUE,
  EYEBROW,
  HINT,
  HINT_ROW,
  META,
  NOTE,
  NOTE_LABEL,
  REVEAL,
  SAY,
  STREAK,
  SUB,
  chipStyle,
  plural,
} from './recall_styles';

// ---------------------------------------------------------------------------
// Focus check-in
// ---------------------------------------------------------------------------

const QUESTION: CSSProperties = {
  margin: 0,
  fontSize: 19,
  fontWeight: 700,
  lineHeight: 1.35,
  letterSpacing: '-0.3px',
  color: colors.text,
};

const WEEK: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(7, 1fr)',
  gap: 6,
  marginTop: 4,
};

const DAY: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: 5,
  fontSize: 10.5,
  fontWeight: 700,
  color: colors.faint,
};

function dot(done: boolean | null, isToday: boolean): CSSProperties {
  return {
    width: 26,
    height: 26,
    borderRadius: '50%',
    display: 'grid',
    placeItems: 'center',
    color: '#FFFFFF',
    background: done ? colors.green : 'transparent',
    border: `2px ${isToday && !done ? 'dashed' : 'solid'} ${
      done ? colors.green : isToday ? colors.primary : colors.line
    }`,
  };
}

function weekdayInitial(isoDate: string): string {
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString(undefined, {
    weekday: 'narrow',
  });
}

export function CheckinView({ checkin }: { checkin: RecallCheckin }) {
  const lastIndex = checkin.last7.length - 1;
  return (
    <Card padding={18}>
      <div style={CARD_STACK}>
        <span style={chipStyle('focus')}>Focus check-in</span>
        <h2 style={CUE}>{checkin.title}</h2>
        <p style={QUESTION}>{checkin.question}</p>
        {checkin.why && (
          <div style={NOTE}>
            <span style={NOTE_LABEL}>Why</span>
            {checkin.why}
          </div>
        )}
        <div style={WEEK} aria-label="Last 7 days">
          {checkin.last7.map((day, i) => (
            <div key={day.date} style={DAY}>
              <span style={dot(day.done === true, i === lastIndex)}>
                {day.done === true && (
                  <IonIcon icon={checkmark} style={{ fontSize: 14 }} aria-hidden />
                )}
              </span>
              {weekdayInitial(day.date)}
            </div>
          ))}
        </div>
        <span style={STREAK}>
          {checkin.streak > 0
            ? `${plural(checkin.streak, 'day')} streak`
            : 'Start your streak today'}
        </span>
      </div>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Practice card (prompt → reveal)
// ---------------------------------------------------------------------------

const STEPS: CSSProperties = {
  margin: 0,
  padding: 0,
  listStyle: 'none',
  display: 'flex',
  flexDirection: 'column',
  gap: 8,
};

const STEP: CSSProperties = {
  display: 'flex',
  gap: 10,
  fontSize: 14,
  lineHeight: 1.4,
  color: colors.text,
};

const STEP_NUM: CSSProperties = {
  flex: 'none',
  width: 22,
  height: 22,
  borderRadius: '50%',
  display: 'grid',
  placeItems: 'center',
  fontSize: 11.5,
  fontWeight: 800,
  color: '#15803D',
  background: 'rgba(22, 163, 74, 0.11)',
};

function KindChips({ card, label }: { card: RecallCard; label: string }) {
  return (
    <div style={CHIP_ROW}>
      <span style={chipStyle(card.kind)}>{label}</span>
      {card.isNew && <span style={chipStyle('new')}>New</span>}
    </div>
  );
}

export interface CardViewProps {
  card: RecallCard;
  revealed: boolean;
}

export function CardView({ card, revealed }: CardViewProps) {
  if (card.kind === 'line') {
    const { line } = card;
    const isGoal = line.cueType === 'goal';
    return (
      <>
        <Card padding={18}>
          <div style={CARD_STACK}>
            <KindChips card={card} label="Line" />
            <span style={EYEBROW}>{isGoal ? 'Goal' : 'She says'}</span>
            <h2 style={CUE}>{isGoal ? line.cueText : `“${line.cueText}”`}</h2>
            {line.hint && (
              <div style={HINT_ROW}>
                <span>Answer with</span>
                <span style={HINT}>{line.hint}</span>
              </div>
            )}
            {revealed && (
              <div className="riffy-rise" style={REVEAL}>
                <span style={EYEBROW}>Your line</span>
                <p style={ANSWER}>“{line.text}”</p>
                {line.deliveryNote && (
                  <div style={NOTE}>
                    <span style={NOTE_LABEL}>How to say it</span>
                    {line.deliveryNote}
                  </div>
                )}
                {line.cueLineCount > 1 && (
                  <span style={META}>
                    {line.position} of {line.cueLineCount} lines on this cue
                  </span>
                )}
              </div>
            )}
          </div>
        </Card>
        {!revealed && <p style={SAY}>Say your line out loud, then reveal.</p>}
      </>
    );
  }

  if (card.kind === 'concept') {
    const { concept } = card;
    return (
      <>
        <Card padding={18}>
          <div style={CARD_STACK}>
            <KindChips card={card} label="Concept" />
            <span style={EYEBROW}>Which concept is this?</span>
            <p style={BODY_TEXT}>{concept.scenario}</p>
            {revealed && (
              <div className="riffy-rise" style={REVEAL}>
                <span style={EYEBROW}>Concept</span>
                <p style={ANSWER}>{concept.name}</p>
                <p style={SUB}>{concept.definition}</p>
                {concept.scenarioCount > 1 && (
                  <span style={META}>
                    Scenario {concept.scenarioNumber} of {concept.scenarioCount}
                  </span>
                )}
              </div>
            )}
          </div>
        </Card>
        {!revealed && <p style={SAY}>Name it out loud, then reveal.</p>}
      </>
    );
  }

  const { routine } = card;
  return (
    <>
      <Card padding={18}>
        <div style={CARD_STACK}>
          <KindChips card={card} label="Routine" />
          <span style={EYEBROW}>Recall the steps</span>
          <h2 style={CUE}>{routine.name}</h2>
          {revealed && (
            <div className="riffy-rise" style={REVEAL}>
              <ol style={STEPS}>
                {routine.steps.map((text, i) => (
                  <li key={i} style={STEP}>
                    <span style={STEP_NUM}>{i + 1}</span>
                    <span>{text}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      </Card>
      {!revealed && <p style={SAY}>Say the steps out loud, then reveal.</p>}
    </>
  );
}

// ---------------------------------------------------------------------------
// Done
// ---------------------------------------------------------------------------

const DONE_HERO: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: 12,
  padding: '28px 0 22px',
  textAlign: 'center',
};

const DONE_RING: CSSProperties = {
  width: 104,
  height: 104,
  borderRadius: '50%',
  display: 'grid',
  placeItems: 'center',
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  boxShadow: '0 14px 30px rgba(249, 115, 22, 0.16)',
};

const DONE_TITLE: CSSProperties = {
  margin: 0,
  fontSize: 26,
  fontWeight: 800,
  letterSpacing: '-0.6px',
  color: colors.text,
};

const KV: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  fontSize: 14,
  padding: '10px 0',
};

export interface DoneViewProps {
  cards: number;
  checkins: number;
  outlook: RecallOutlook | null;
}

export function DoneView({ cards, checkins, outlook }: DoneViewProps) {
  const rows: [string, string][] = [
    ['Next session', 'Tomorrow'],
    ['Due tomorrow', outlook ? plural(outlook.dueTomorrow, 'card') : '…'],
    ['New items waiting', outlook ? String(outlook.newWaiting) : '…'],
  ];
  return (
    <>
      <div style={DONE_HERO}>
        <div className="riffy-rise" style={DONE_RING}>
          <RiffyMark size={48} />
        </div>
        <h2 style={DONE_TITLE}>Done for today</h2>
        <p style={SUB}>
          {plural(cards, 'card')} and {plural(checkins, 'check-in')}.
        </p>
      </div>
      <Card padding="4px 16px">
        {rows.map(([label, value], i) => (
          <div
            key={label}
            style={{ ...KV, borderTop: i > 0 ? `1px solid ${colors.line}` : 'none' }}
          >
            <span style={{ color: colors.muted }}>{label}</span>
            <b style={{ color: colors.text, fontVariantNumeric: 'tabular-nums' }}>{value}</b>
          </div>
        ))}
      </Card>
    </>
  );
}
