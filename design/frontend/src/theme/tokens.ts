/**
 * Design tokens for the "Light & Warm" theme.
 * Single source of truth for TS code — import from '@/theme/tokens'.
 * The matching CSS variables live in ionic_variables.css.
 */

export const colors = {
  /** Page background — soft off-white */
  bg: '#F7F8FA',
  /** Cards / sheets */
  surface: '#FFFFFF',
  /** Primary text */
  text: '#2B2F3A',
  /** Secondary text */
  muted: '#6B7589',
  /** Hints / inactive */
  faint: '#9AA3B2',
  /** Borders */
  line: '#E5EAF1',
  /** Secondary / muted fills */
  tint: '#F8FAFC',
  /** CTAs, gradients, celebration */
  accent: '#F97316',
  /** Primary buttons, links */
  primary: '#3B82F6',
  /** Active tab / selected state */
  active: '#0A8FF2',
  /** Streak / medium */
  amber: '#F5A30A',
  /** Success / easy */
  green: '#16A34A',
  /** Calm / telegram */
  sky: '#0EA5E9',
  /** Destructive / hard */
  red: '#EF4444',
} as const;

export const gradients = {
  /** Primary CTA warm gradient */
  warmCta: 'linear-gradient(135deg, #F97316, #F7C13B)',
  /** Active tab indicator gradient */
  activeTab: 'linear-gradient(135deg, #0A8FF2, #F97316)',
} as const;

export const shadows = {
  /** Soft accent shadow */
  soft: '0 4px 20px -2px rgba(249, 115, 22, 0.10)',
  /** Warm elevated shadow */
  warm: '0 8px 30px -4px rgba(249, 115, 22, 0.20)',
} as const;

export const radius = {
  md: '12px',
} as const;

export const font = {
  family: 'Inter, system-ui, sans-serif',
} as const;

/** Full token map — all sub-objects collected for convenience. */
const tokens = {
  colors,
  gradients,
  shadows,
  radius,
  font,
} as const;

export default tokens;
