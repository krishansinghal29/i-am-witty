import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { checkmark, close } from 'ionicons/icons';
import { colors } from '@/theme/tokens';

export type DayState = 'done' | 'today' | 'missed' | 'upcoming';

export interface WeekDay {
  /** Defaults to the Su–Sa label for the day's index. */
  label?: string;
  state: DayState;
}

export interface WeekStripProps {
  days: WeekDay[];
}

const DEFAULT_LABELS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

const CELL_BASE: CSSProperties = {
  width: 34,
  height: 34,
  borderRadius: '50%',
  display: 'grid',
  placeItems: 'center',
  fontSize: 13,
  fontWeight: 700,
};

function cellStyle(state: DayState): CSSProperties {
  switch (state) {
    case 'done':
      return {
        ...CELL_BASE,
        background: 'rgba(22, 163, 74, 0.12)',
        color: colors.green,
        border: '1px solid rgba(22, 163, 74, 0.3)',
      };
    case 'today':
      return {
        ...CELL_BASE,
        background: `linear-gradient(150deg, ${colors.primary}, ${colors.active})`,
        color: '#FFFFFF',
        boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.16), 0 6px 14px rgba(59, 130, 246, 0.4)',
      };
    case 'missed':
      return {
        ...CELL_BASE,
        background: colors.surface,
        color: colors.faint,
        border: `1px solid ${colors.line}`,
      };
    case 'upcoming':
    default:
      return {
        ...CELL_BASE,
        background: colors.surface,
        color: colors.faint,
        border: `1.5px dashed ${colors.line}`,
      };
  }
}

/** Su–Sa progress strip with per-day done / today / missed / upcoming states. */
export function WeekStrip({ days }: WeekStripProps) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
      {days.map((day, index) => {
        const label = day.label ?? DEFAULT_LABELS[index] ?? '';
        const isToday = day.state === 'today';
        return (
          <div
            key={`${label}-${index}`}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 7, flex: 1 }}
          >
            <span
              style={{
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: '0.4px',
                color: isToday ? colors.active : colors.faint,
              }}
            >
              {label}
            </span>
            <span style={cellStyle(day.state)}>
              {day.state === 'done' && <IonIcon icon={checkmark} style={{ fontSize: 16 }} aria-hidden />}
              {day.state === 'missed' && <IonIcon icon={close} style={{ fontSize: 14 }} aria-hidden />}
              {day.state === 'upcoming' && '·'}
            </span>
          </div>
        );
      })}
    </div>
  );
}
