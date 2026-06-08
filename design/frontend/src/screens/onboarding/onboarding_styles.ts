import type { CSSProperties } from 'react';
import { colors } from '@/theme/tokens';

/** Shared step layout/typography for the onboarding flow (calm + warm). */

export const STEP_BODY: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  flex: 1,
  padding: '4px 22px 26px',
  minHeight: '100%',
};

export const KICKER: CSSProperties = {
  fontWeight: 700,
  fontSize: 11,
  letterSpacing: '1.6px',
  textTransform: 'uppercase',
  color: colors.active,
};

export const QUESTION: CSSProperties = {
  fontWeight: 700,
  fontSize: 27,
  lineHeight: 1.1,
  letterSpacing: '-0.5px',
  color: colors.text,
  marginTop: 9,
};

export const SUBTITLE: CSSProperties = {
  fontSize: 13.5,
  color: colors.muted,
  lineHeight: 1.5,
  maxWidth: '32ch',
  marginTop: 9,
};

export const PUSH_DOWN: CSSProperties = { marginTop: 'auto' };

export const PRIVACY: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 7,
  fontSize: 12,
  color: colors.faint,
  fontWeight: 500,
  marginTop: 12,
};

export const ERROR_LINE: CSSProperties = {
  textAlign: 'center',
  fontSize: 12.5,
  color: colors.red,
  fontWeight: 600,
  marginTop: 10,
};

export const CENTER_HERO: CSSProperties = {
  textAlign: 'center',
  marginTop: 6,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
};
