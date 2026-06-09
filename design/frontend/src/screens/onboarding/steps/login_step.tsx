import type { CSSProperties } from 'react';
import { IonIcon, IonSpinner } from '@ionic/react';
import { lockClosedOutline, logoApple, logoGoogle, sparkles } from 'ionicons/icons';
import { colors, radius } from '@/theme/tokens';
import { AppError } from '@/data/errors/app_error';
import {
  CENTER_HERO,
  ERROR_LINE,
  PRIVACY,
  PUSH_DOWN,
  STEP_BODY,
} from '@/screens/onboarding/onboarding_styles';

export interface LoginStepProps {
  onApple: () => void;
  onGoogle: () => void;
  isLoading: boolean;
  error: unknown;
}

const SPARK: CSSProperties = {
  width: 92,
  height: 92,
  margin: '10px auto 0',
  borderRadius: 28,
  display: 'grid',
  placeItems: 'center',
  background: 'rgba(249, 115, 22, 0.12)',
  border: '1px solid rgba(249, 115, 22, 0.34)',
  boxShadow: '0 14px 34px rgba(249, 115, 22, 0.22)',
  color: colors.accent,
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

export function LoginStep({ onApple, onGoogle, isLoading, error }: LoginStepProps) {
  return (
    <div style={STEP_BODY}>
      <div style={CENTER_HERO}>
        <div style={SPARK} aria-hidden>
          <IonIcon icon={sparkles} style={{ fontSize: 40 }} />
        </div>
        <h2 style={HEADING}>Create your account</h2>
        <p style={SUB}>
          One tap to save your progress and pick up right where you left off on
          any device.
        </p>
      </div>

      <div style={{ ...AUTH_GROUP, ...PUSH_DOWN }}>
        <button
          type="button"
          className="riffy-pressable"
          style={APPLE_BTN}
          onClick={onApple}
          disabled={isLoading}
        >
          {isLoading ? (
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
          className="riffy-pressable"
          style={GOOGLE_BTN}
          onClick={onGoogle}
          disabled={isLoading}
        >
          <IonIcon icon={logoGoogle} style={{ fontSize: 20 }} aria-hidden />
          Continue with Google
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
