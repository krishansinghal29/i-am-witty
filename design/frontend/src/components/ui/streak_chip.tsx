import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { flame } from 'ionicons/icons';
import { colors } from '@/theme/tokens';

export interface StreakChipProps {
  count: number;
}

const CHIP_STYLE: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  padding: '6px 13px 6px 10px',
  borderRadius: 999,
  fontWeight: 700,
  fontSize: 16,
  lineHeight: 1,
  color: colors.amber,
  background: 'rgba(245, 163, 10, 0.08)',
  border: '1px solid rgba(245, 163, 10, 0.4)',
};

/** Amber flame chip showing the user's current streak count. */
export function StreakChip({ count }: StreakChipProps) {
  return (
    <span style={CHIP_STYLE} aria-label={`${count} day streak`}>
      <IonIcon icon={flame} style={{ fontSize: 18, color: colors.amber }} aria-hidden />
      {count}
    </span>
  );
}
