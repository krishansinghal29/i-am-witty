import { useCallback } from 'react';
import type { CSSProperties } from 'react';
import { IonIcon, IonSpinner } from '@ionic/react';
import {
  flame,
  lockClosedOutline,
  logoApple,
  logoGoogle,
} from 'ionicons/icons';
import { colors, radius } from '@/theme/tokens';
import { AppError } from '@/data/errors/app_error';
import { useLinkAccount } from '@/features/identity/use_link_account';
import {
  CENTER_HERO,
  ERROR_LINE,
  PRIVACY,
  PUSH_DOWN,
  STEP_BODY,
} from '@/screens/onboarding/onboarding_styles';

export interface LoginStepProps {
  /** Called after a successful link OR when the user chooses "Not now". */
  onContinue: () => void;
}

const FLAME: CSSProperties = {
  position: 'relative',
  width: 92,
  height: 92,
  margin: '10px auto 0',
  borderRadius: 28,
  display: 'grid',
  placeItems: 'center',
  background: 'rgba(249, 115, 22, 0.12)',
  border: '1px solid rgba(249, 115, 22, 0.34)',
  boxShadow: '0 14px 34px rgba(249, 115, 22, 0.22)',
};

const DAY_PILL: CSSProperties = {
  position: 'absolute',
  bottom: -10,
  fontWeight: 800,
  fontSize: 14,
  color: '#FFFFFF',
  background: colors.amber,
  padding: '3px 12px',
  borderRadius: 999,
  boxShadow: '0 6px 14px rgba(245, 163, 10, 0.4)',
};

const HEADING: CSSProperties = {
  fontWeight: 700,
  fontSize: 25,
  letterSpacing: '-0.3px',
  color: colors.text,
  marginTop: 26,
};

const SUB: CSSProperties = {
  fontSize: 13.5,
  color: colors.muted,
  lineHeight: 1.5,
  maxWidth: '30ch',
  margin: '9px auto 0',
};

const AUTH_GROUP: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 11,
};

const AUTH_BTN_BASE: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 11,
  width: '100%',
  padding: '15px',
  borderRadius: radius.md,
  fontWeight: 600,
  fontSize: 16,
  cursor: 'pointer',
  border: '1px solid transparent',
};

const APPLE_BTN: CSSProperties = {
  ...AUTH_BTN_BASE,
  background: '#0A0710',
  color: '#FFFFFF',
};

const GOOGLE_BTN: CSSProperties = {
  ...AUTH_BTN_BASE,
  background: '#FFFFFF',
  color: '#1F1F1F',
  border: '1px solid #D8E0EA',
  boxShadow: '0 2px 8px rgba(17, 24, 39, 0.06)',
};

const NOT_NOW: CSSProperties = {
  ...AUTH_BTN_BASE,
  background: 'transparent',
  color: colors.muted,
  border: `1px solid ${colors.line}`,
  fontWeight: 600,
};

export function LoginStep({ onContinue }: LoginStepProps) {
  const { linkWithApple, linkWithGoogle, isLinking, error } = useLinkAccount();

  const handleApple = useCallback(async () => {
    try {
      await linkWithApple();
      onContinue();
    } catch {
      // Surfaced inline via `error`; "Not now" stays available.
    }
  }, [linkWithApple, onContinue]);

  const handleGoogle = useCallback(async () => {
    try {
      await linkWithGoogle();
      onContinue();
    } catch {
      // Surfaced inline via `error`.
    }
  }, [linkWithGoogle, onContinue]);

  return (
    <div style={STEP_BODY}>
      <div style={CENTER_HERO}>
        <div style={FLAME} aria-hidden>
          <IonIcon icon={flame} style={{ fontSize: 42, color: colors.accent }} />
          <span style={DAY_PILL}>Day 1</span>
        </div>
        <h2 style={HEADING}>Save your Day 1 streak?</h2>
        <p style={SUB}>
          Lock in today’s win so it’s still here tomorrow. Takes one tap — and your
          progress so far comes with you.
        </p>
      </div>

      <div style={{ ...AUTH_GROUP, ...PUSH_DOWN }}>
        <button
          type="button"
          className="witty-pressable"
          style={APPLE_BTN}
          onClick={() => void handleApple()}
          disabled={isLinking}
        >
          {isLinking ? (
            <IonSpinner name="crescent" />
          ) : (
            <>
              <IonIcon icon={logoApple} style={{ fontSize: 20 }} aria-hidden />
              Continue with Apple
            </>
          )}
        </button>

        <button
          type="button"
          className="witty-pressable"
          style={GOOGLE_BTN}
          onClick={() => void handleGoogle()}
          disabled={isLinking}
        >
          <IonIcon icon={logoGoogle} style={{ fontSize: 20 }} aria-hidden />
          Continue with Google
        </button>

        <button
          type="button"
          className="witty-pressable"
          style={NOT_NOW}
          onClick={onContinue}
          disabled={isLinking}
        >
          Not now
        </button>

        {error != null && (
          <p style={ERROR_LINE}>{AppError.from(error).userMessage}</p>
        )}

        <div style={PRIVACY}>
          <IonIcon icon={lockClosedOutline} aria-hidden />
          We never post anything. Your practice stays yours.
        </div>
      </div>
    </div>
  );
}
