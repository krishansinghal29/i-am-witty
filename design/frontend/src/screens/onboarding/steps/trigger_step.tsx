import type { CSSProperties } from 'react';
import { IonIcon, IonSpinner } from '@ionic/react';
import { chevronForward } from 'ionicons/icons';
import { colors, radius, shadows } from '@/theme/tokens';
import { AppError } from '@/data/errors/app_error';
import { TRIGGER_OPTIONS } from '@/screens/onboarding/triggers';
import type { TriggerOption } from '@/screens/onboarding/triggers';
import {
  ERROR_LINE,
  KICKER,
  QUESTION,
  STEP_BODY,
  SUBTITLE,
} from '@/screens/onboarding/onboarding_styles';

export interface TriggerStepProps {
  selectedTrigger: string | null;
  isSaving: boolean;
  error: unknown;
  onSelect: (value: string) => void;
}

const LIST: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 10,
  marginTop: 22,
};

const ROW: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 13,
  width: '100%',
  textAlign: 'left',
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: radius.md,
  boxShadow: shadows.soft,
  padding: '13px 14px',
  color: colors.text,
  cursor: 'pointer',
};

const EMOJI: CSSProperties = {
  width: 42,
  height: 42,
  borderRadius: 13,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  fontSize: 21,
  background: 'rgba(59, 130, 246, 0.10)',
  border: '1px solid rgba(59, 130, 246, 0.22)',
};

const LABEL: CSSProperties = { flex: 1, fontWeight: 600, fontSize: 16 };

function OptionRow({
  option,
  pending,
  disabled,
  onSelect,
}: {
  option: TriggerOption;
  pending: boolean;
  disabled: boolean;
  onSelect: (value: string) => void;
}) {
  return (
    <button
      type="button"
      className="witty-pressable"
      style={{ ...ROW, opacity: disabled && !pending ? 0.55 : 1 }}
      disabled={disabled}
      onClick={() => onSelect(option.value)}
      aria-label={option.label}
    >
      <span style={EMOJI} aria-hidden>
        {option.emoji}
      </span>
      <span style={LABEL}>{option.label}</span>
      {pending ? (
        <IonSpinner name="crescent" style={{ color: colors.primary }} />
      ) : (
        <IonIcon icon={chevronForward} style={{ color: colors.faint, fontSize: 18 }} aria-hidden />
      )}
    </button>
  );
}

export function TriggerStep({ selectedTrigger, isSaving, error, onSelect }: TriggerStepProps) {
  return (
    <div style={STEP_BODY}>
      <span style={KICKER}>Let’s make this yours</span>
      <h1 style={QUESTION}>Where do you want to feel quicker?</h1>
      <p style={SUBTITLE}>
        Pick one — we’ll start you with a tiny win for exactly that. You can change
        it any time.
      </p>

      <div style={LIST}>
        {TRIGGER_OPTIONS.map((option) => (
          <OptionRow
            key={option.value}
            option={option}
            pending={isSaving && selectedTrigger === option.value}
            disabled={isSaving}
            onSelect={onSelect}
          />
        ))}
      </div>

      {error != null && (
        <p style={ERROR_LINE}>{AppError.from(error).userMessage}</p>
      )}
    </div>
  );
}
