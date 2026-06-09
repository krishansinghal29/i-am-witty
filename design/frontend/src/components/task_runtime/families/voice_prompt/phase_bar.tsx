import type { CSSProperties } from 'react';
import { colors, gradients } from '@/theme/tokens';
import type { RuntimePhase } from '@/state/stores/runtime_store';
import { phaseStatus } from './phase_machine';
import type { PhaseStep, PhaseStatus } from './phase_machine';

export interface PhaseBarProps {
  steps: PhaseStep[];
  current: RuntimePhase;
  onSelect?: (phase: RuntimePhase) => void;
}

const ROW: CSSProperties = {
  display: 'flex',
  gap: 8,
  padding: '4px 18px 12px',
};

function barStyle(status: PhaseStatus): CSSProperties {
  const base: CSSProperties = {
    height: 5,
    borderRadius: 4,
    transition: 'background 0.25s ease',
  };
  if (status === 'done') return { ...base, background: colors.green };
  if (status === 'active') return { ...base, background: gradients.activeTab };
  return { ...base, background: colors.line };
}

function labelStyle(status: PhaseStatus): CSSProperties {
  return {
    fontSize: 10.5,
    fontWeight: 700,
    letterSpacing: 0.2,
    color:
      status === 'done'
        ? colors.green
        : status === 'active'
          ? colors.active
          : colors.faint,
  };
}

/** Brief · Respond · Reflect indicator. Done phases are tappable to revisit. */
export function PhaseBar({ steps, current, onSelect }: PhaseBarProps) {
  return (
    <nav style={ROW} aria-label="Task progress">
      {steps.map((step) => {
        const status = phaseStatus(step.key, current);
        const interactive = onSelect != null && status !== 'upcoming';
        return (
          <button
            key={step.key}
            type="button"
            onClick={interactive ? () => onSelect?.(step.key) : undefined}
            disabled={!interactive}
            className={interactive ? 'riffy-pressable' : undefined}
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              gap: 6,
              textAlign: 'left',
              border: 'none',
              background: 'transparent',
              padding: 0,
              cursor: interactive ? 'pointer' : 'default',
            }}
            aria-current={status === 'active' ? 'step' : undefined}
          >
            <span style={barStyle(status)} />
            <span style={labelStyle(status)}>{step.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
