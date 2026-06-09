import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { mic, stop } from 'ionicons/icons';
import { colors, gradients, shadows } from '@/theme/tokens';
import { useReducedMotion } from './use_reduced_motion';
import './ui.css';

export interface RecordRingProps {
  recording: boolean;
  /** 0..1 fill of the progress ring (e.g. elapsed / limit). */
  progress?: number;
  onPress: () => void;
  disabled?: boolean;
}

const SIZE = 168;
const STROKE = 8;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
const BUTTON_SIZE = 108;

function buttonStyle(recording: boolean, disabled: boolean): CSSProperties {
  return {
    width: BUTTON_SIZE,
    height: BUTTON_SIZE,
    borderRadius: '50%',
    border: 'none',
    padding: 0,
    background: recording ? colors.accent : gradients.warmCta,
    boxShadow: shadows.warm,
    display: 'grid',
    placeItems: 'center',
    opacity: disabled ? 0.5 : 1,
    cursor: disabled ? 'not-allowed' : 'pointer',
  };
}

/** Big circular record button with a progress + pulse ring (reduced-motion aware). */
export function RecordRing({ recording, progress, onPress, disabled = false }: RecordRingProps) {
  const reduced = useReducedMotion();
  const clamped = Math.max(0, Math.min(1, progress ?? 0));
  const showPulse = recording && !reduced && !disabled;

  return (
    <div style={{ position: 'relative', width: SIZE, height: SIZE, display: 'grid', placeItems: 'center' }}>
      {showPulse && (
        <span
          className="riffy-ring-pulse"
          style={{
            position: 'absolute',
            width: SIZE,
            height: SIZE,
            borderRadius: '50%',
            background: 'rgba(249, 115, 22, 0.18)',
          }}
        />
      )}

      <svg width={SIZE} height={SIZE} style={{ position: 'absolute', transform: 'rotate(-90deg)' }}>
        <circle cx={SIZE / 2} cy={SIZE / 2} r={RADIUS} fill="none" stroke={colors.line} strokeWidth={STROKE} />
        {clamped > 0 && (
          <circle
            cx={SIZE / 2}
            cy={SIZE / 2}
            r={RADIUS}
            fill="none"
            stroke={colors.accent}
            strokeWidth={STROKE}
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={CIRCUMFERENCE * (1 - clamped)}
          />
        )}
      </svg>

      <button
        type="button"
        onClick={onPress}
        disabled={disabled}
        aria-label={recording ? 'Stop recording' : 'Start recording'}
        aria-pressed={recording}
        className="riffy-pressable"
        style={buttonStyle(recording, disabled)}
      >
        <IonIcon icon={recording ? stop : mic} style={{ fontSize: 40, color: '#FFFFFF' }} aria-hidden />
      </button>
    </div>
  );
}
