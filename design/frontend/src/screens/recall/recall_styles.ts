import type { CSSProperties } from 'react';
import { colors } from '@/theme/tokens';

/** Shared typography, chips and card parts for the Recall tab and session. */

export type RecallChipTone = 'line' | 'concept' | 'routine' | 'focus' | 'new';

/** Each kind gets its own tint so the deck reads at a glance. */
const TONES: Record<RecallChipTone, { color: string; background: string }> = {
  line: { color: '#C2410C', background: 'rgba(249, 115, 22, 0.11)' },
  concept: { color: '#1D4ED8', background: 'rgba(59, 130, 246, 0.11)' },
  routine: { color: '#15803D', background: 'rgba(22, 163, 74, 0.11)' },
  focus: { color: '#B45309', background: 'rgba(245, 163, 10, 0.16)' },
  new: { color: colors.muted, background: colors.tint },
};

export function chipStyle(tone: RecallChipTone): CSSProperties {
  return {
    display: 'inline-flex',
    alignItems: 'center',
    alignSelf: 'flex-start',
    padding: '4px 9px',
    borderRadius: 999,
    fontSize: 11,
    fontWeight: 700,
    whiteSpace: 'nowrap',
    color: TONES[tone].color,
    background: TONES[tone].background,
    border: tone === 'new' ? `1px solid ${colors.line}` : 'none',
  };
}

export function plural(count: number, one: string, many = `${one}s`): string {
  return `${count} ${count === 1 ? one : many}`;
}

export const CHIP_ROW: CSSProperties = { display: 'flex', gap: 6, flexWrap: 'wrap' };

export const CARD_STACK: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 10,
};

export const EYEBROW: CSSProperties = {
  fontSize: 10.5,
  fontWeight: 800,
  letterSpacing: '1px',
  textTransform: 'uppercase',
  color: colors.faint,
};

export const CUE: CSSProperties = {
  margin: 0,
  fontSize: 22,
  fontWeight: 700,
  letterSpacing: '-0.4px',
  lineHeight: 1.28,
  color: colors.text,
  textWrap: 'balance',
};

export const BODY_TEXT: CSSProperties = {
  margin: 0,
  fontSize: 16,
  fontWeight: 500,
  lineHeight: 1.55,
  color: colors.text,
};

export const HINT_ROW: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 8,
  flexWrap: 'wrap',
  fontSize: 12,
  fontWeight: 600,
  color: colors.muted,
};

export const HINT: CSSProperties = {
  display: 'inline-flex',
  padding: '6px 12px',
  borderRadius: 999,
  fontSize: 13,
  fontWeight: 700,
  color: '#C2410C',
  background: 'rgba(249, 115, 22, 0.11)',
};

export const REVEAL: CSSProperties = {
  borderTop: `1px dashed ${colors.line}`,
  paddingTop: 14,
  marginTop: 4,
  display: 'flex',
  flexDirection: 'column',
  gap: 10,
};

export const ANSWER: CSSProperties = {
  margin: 0,
  fontSize: 20,
  fontWeight: 800,
  letterSpacing: '-0.3px',
  lineHeight: 1.3,
  color: colors.text,
};

export const SUB: CSSProperties = {
  margin: 0,
  fontSize: 13.5,
  lineHeight: 1.45,
  color: colors.muted,
};

export const NOTE: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 3,
  fontSize: 13,
  lineHeight: 1.45,
  color: colors.text,
  background: colors.tint,
  border: `1px solid ${colors.line}`,
  borderRadius: 12,
  padding: '10px 12px',
};

export const NOTE_LABEL: CSSProperties = {
  fontSize: 10.5,
  fontWeight: 800,
  letterSpacing: '0.8px',
  textTransform: 'uppercase',
  color: colors.muted,
};

export const META: CSSProperties = { fontSize: 12, fontWeight: 600, color: colors.faint };

export const SAY: CSSProperties = {
  margin: '14px 0 0',
  fontSize: 13,
  lineHeight: 1.45,
  color: colors.muted,
  textAlign: 'center',
};

export const STREAK: CSSProperties = { fontSize: 12, fontWeight: 700, color: colors.amber };
