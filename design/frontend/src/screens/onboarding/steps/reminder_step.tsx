import { useCallback, useState } from 'react';
import type { CSSProperties } from 'react';
import { IonIcon, IonSpinner } from '@ionic/react';
import { colors, radius, shadows } from '@/theme/tokens';
import { AppError } from '@/data/errors/app_error';
import { useReminder } from '@/features/reminders/use_reminder';
import type { SaveReminderInput } from '@/features/reminders/use_reminder';
import {
  ERROR_LINE,
  KICKER,
  PUSH_DOWN,
  QUESTION,
  STEP_BODY,
  SUBTITLE,
} from '@/screens/onboarding/onboarding_styles';

export interface ReminderStepProps {
  onContinue: () => void;
}

interface TimeChoice {
  id: string;
  emoji: string;
  label: string;
  payload: SaveReminderInput;
}

const CHOICES: TimeChoice[] = [
  { id: 'before_work', emoji: '☀️', label: 'Before work', payload: { status: 'enabled', timingKey: 'before_work' } },
  { id: 'before_going_out', emoji: '🌆', label: 'Before going out', payload: { status: 'enabled', timingKey: 'before_going_out' } },
  { id: 'after_dinner', emoji: '🍽️', label: 'After dinner', payload: { status: 'enabled', timingKey: 'after_dinner' } },
  { id: 'evening', emoji: '🕗', label: '8:00 PM', payload: { status: 'enabled', localTime: '20:00' } },
];

const GRID: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 11,
  marginTop: 22,
};

const TILE: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 11,
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: radius.md,
  boxShadow: shadows.soft,
  padding: '14px 13px',
  color: colors.text,
  cursor: 'pointer',
  textAlign: 'left',
};

const SKIP: CSSProperties = {
  display: 'block',
  width: '100%',
  textAlign: 'center',
  padding: 12,
  fontSize: 13.5,
  fontWeight: 600,
  color: colors.muted,
  background: 'transparent',
  border: 'none',
  cursor: 'pointer',
};

export function ReminderStep({ onContinue }: ReminderStepProps) {
  const { save, skip, isSaving, error } = useReminder();
  const [pendingId, setPendingId] = useState<string | null>(null);

  const choose = useCallback(
    async (choice: TimeChoice) => {
      setPendingId(choice.id);
      try {
        await save(choice.payload);
        onContinue();
      } catch {
        // Surfaced inline via `error`; the user can retry or skip.
      } finally {
        setPendingId(null);
      }
    },
    [save, onContinue],
  );

  const handleSkip = useCallback(async () => {
    setPendingId('skip');
    try {
      await skip();
      onContinue();
    } catch {
      // Even if saving the skip fails, let the user move on.
      onContinue();
    } finally {
      setPendingId(null);
    }
  }, [skip, onContinue]);

  return (
    <div style={STEP_BODY}>
      <span style={KICKER}>One last thing</span>
      <h1 style={QUESTION}>When should we warm you up?</h1>
      <p style={SUBTITLE}>A tiny nudge, only when you want it. No spam, ever.</p>

      <div style={GRID}>
        {CHOICES.map((choice) => {
          const pending = pendingId === choice.id;
          return (
            <button
              key={choice.id}
              type="button"
              className="witty-pressable"
              style={{ ...TILE, opacity: isSaving && !pending ? 0.55 : 1 }}
              disabled={isSaving}
              onClick={() => void choose(choice)}
              aria-label={choice.label}
            >
              {pending ? (
                <IonSpinner name="crescent" style={{ color: colors.primary }} />
              ) : (
                <span style={{ fontSize: 20 }} aria-hidden>
                  {choice.emoji}
                </span>
              )}
              <span style={{ fontWeight: 600, fontSize: 14.5, lineHeight: 1.2 }}>
                {choice.label}
              </span>
            </button>
          );
        })}
      </div>

      {error != null && <p style={ERROR_LINE}>{AppError.from(error).userMessage}</p>}

      <div style={PUSH_DOWN}>
        <button
          type="button"
          style={SKIP}
          onClick={() => void handleSkip()}
          disabled={isSaving}
        >
          {pendingId === 'skip' ? 'One sec…' : 'Not now'}
        </button>
      </div>
    </div>
  );
}
