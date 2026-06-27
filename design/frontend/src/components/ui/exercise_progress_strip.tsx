import type { CSSProperties } from 'react';
import { colors, gradients } from '@/theme/tokens';

/**
 * Shared "X / N" rep-progress indicator: an optional count line plus a row of
 * fill-up dots (one per rep). Used by both the roleplay shell (landed/target,
 * dots only) and the single-prompt voice shell (completed/total, count + dots).
 *
 * Renders nothing for single-rep exercises (`total <= 1`) so classic
 * single-shot tasks show no bar — the one place this rule lives.
 */
export interface ExerciseProgressStripProps {
  completed: number;
  total: number;
  /** Show the "completed / total" line above the dots. */
  showCount?: boolean;
  /** Small label shown to the left of the count (e.g. "Reps"). */
  label?: string;
  /** Extra styling for the outer container. */
  style?: CSSProperties;
}

export function ExerciseProgressStrip({
  completed,
  total,
  showCount = true,
  label,
  style,
}: ExerciseProgressStripProps) {
  if (total <= 1) return null;
  const filled = Math.min(Math.max(completed, 0), total);

  return (
    <div style={style}>
      {showCount && (
        <div style={COUNT_ROW}>
          {label && <span style={LABEL}>{label}</span>}
          <span style={COUNT}>
            {filled}
            <span style={COUNT_TOTAL}> / {total}</span>
          </span>
        </div>
      )}
      <div style={DOTS}>
        {Array.from({ length: total }).map((_, i) => (
          <span key={i} style={{ ...DOT, background: dotFill(i, filled) }} />
        ))}
      </div>
    </div>
  );
}

/** Filled reps use the active gradient; the current rep is a faint active tint;
 *  the rest are a neutral track. Matches the roleplay strip exactly. */
function dotFill(index: number, filled: number): string {
  if (index < filled) return gradients.activeTab;
  if (index === filled) return 'rgba(10, 143, 242, 0.3)';
  return 'rgba(43, 47, 58, 0.12)';
}

const COUNT_ROW: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: 8,
};

const LABEL: CSSProperties = {
  fontSize: 10,
  fontWeight: 800,
  letterSpacing: 0.8,
  textTransform: 'uppercase',
  color: colors.faint,
};

const COUNT: CSSProperties = {
  marginLeft: 'auto',
  fontWeight: 800,
  fontSize: 13,
  color: colors.active,
};

const COUNT_TOTAL: CSSProperties = {
  color: colors.faint,
  fontWeight: 700,
  fontSize: 12,
};

const DOTS: CSSProperties = {
  display: 'flex',
  gap: 5,
};

const DOT: CSSProperties = {
  flex: 1,
  height: 5,
  borderRadius: 3,
};
