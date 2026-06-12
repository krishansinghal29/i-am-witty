import { useState, type CSSProperties, type FormEvent } from 'react';
import { IonIcon, IonSpinner } from '@ionic/react';
import { lockClosedOutline, logoApple, logoGoogle, sparkles } from 'ionicons/icons';
import { colors, gradients, radius } from '@/theme/tokens';
import { AppError } from '@/data/errors/app_error';
import {
  CENTER_HERO,
  ERROR_LINE,
  PRIVACY,
  PUSH_DOWN,
  STEP_BODY,
} from '@/screens/onboarding/onboarding_styles';

type AuthActionKind = 'apple' | 'google' | 'email-signup' | 'email-login';
type EmailMode = 'signup' | 'login';

export interface LoginStepProps {
  onApple: () => Promise<unknown>;
  onGoogle: () => Promise<unknown>;
  onSignUpEmail: (email: string, password: string) => Promise<unknown>;
  onLogInEmail: (email: string, password: string) => Promise<unknown>;
  onForgotPassword: (email: string) => Promise<unknown>;
  activeAction: AuthActionKind | null;
  error: unknown;
  forgotPasswordState: 'idle' | 'sending' | 'sent' | 'error';
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_PASSWORD = 6;

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
  marginTop: 22,
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

const DIVIDER: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  color: colors.faint,
  fontSize: 11.5,
  fontWeight: 700,
  letterSpacing: '0.6px',
  textTransform: 'uppercase',
  margin: '3px 0',
};

const DIVIDER_LINE: CSSProperties = { flex: 1, height: 1, background: colors.line };

const SEGMENT: CSSProperties = {
  display: 'flex',
  padding: 4,
  gap: 4,
  background: colors.tint,
  border: `1px solid ${colors.line}`,
  borderRadius: radius.md,
};

const EMAIL_FORM: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 10,
};

const INPUT: CSSProperties = {
  width: '100%',
  padding: '14px',
  borderRadius: radius.md,
  border: `1px solid ${colors.line}`,
  background: colors.surface,
  fontSize: 15,
  color: colors.text,
  outline: 'none',
};

const SUBMIT_BTN: CSSProperties = {
  ...AUTH_BTN_BASE,
  background: gradients.warmCta,
  color: '#FFFFFF',
};

const FORGOT_BTN: CSSProperties = {
  alignSelf: 'center',
  background: 'none',
  border: 'none',
  color: colors.primary,
  fontSize: 13,
  fontWeight: 600,
  cursor: 'pointer',
  padding: '2px 4px',
};

const SENT_LINE: CSSProperties = {
  textAlign: 'center',
  fontSize: 12.5,
  color: colors.green,
  fontWeight: 600,
  marginTop: 2,
};

function authBtnStyle(
  base: CSSProperties,
  kind: AuthActionKind,
  active: AuthActionKind | null,
): CSSProperties {
  const isBusy = active !== null;
  const isActive = active === kind;
  return {
    ...base,
    opacity: isBusy && !isActive ? 0.55 : 1,
    cursor: isBusy ? 'not-allowed' : 'pointer',
  };
}

function segBtnStyle(on: boolean): CSSProperties {
  return {
    flex: 1,
    padding: '9px 0',
    borderRadius: 9,
    border: 'none',
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
    background: on ? colors.surface : 'transparent',
    color: on ? colors.text : colors.muted,
    boxShadow: on ? '0 1px 4px rgba(17, 24, 39, 0.08)' : 'none',
  };
}

export function LoginStep({
  onApple,
  onGoogle,
  onSignUpEmail,
  onLogInEmail,
  onForgotPassword,
  activeAction,
  error,
  forgotPasswordState,
}: LoginStepProps) {
  // Local flag so a control disables immediately on tap, before the mutation
  // hook re-renders with its pending state.
  const [pending, setPending] = useState<AuthActionKind | null>(null);
  const [mode, setMode] = useState<EmailMode>('signup');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const active = activeAction ?? pending;
  const isBusy = active !== null;

  const emailKind: AuthActionKind =
    mode === 'signup' ? 'email-signup' : 'email-login';
  const emailBusy = active === emailKind;

  const runOAuth = (kind: AuthActionKind, signIn: () => Promise<unknown>) => {
    if (isBusy) return;
    setLocalError(null);
    setPending(kind);
    void signIn().finally(() => setPending(null));
  };

  const submitEmail = (e: FormEvent) => {
    e.preventDefault();
    if (isBusy) return;
    const trimmed = email.trim();
    if (!EMAIL_RE.test(trimmed)) {
      setLocalError('Enter a valid email address.');
      return;
    }
    if (mode === 'signup' ? password.length < MIN_PASSWORD : password.length === 0) {
      setLocalError(
        mode === 'signup'
          ? `Use at least ${MIN_PASSWORD} characters for your password.`
          : 'Enter your password.',
      );
      return;
    }
    setLocalError(null);
    const run = mode === 'signup' ? onSignUpEmail : onLogInEmail;
    setPending(emailKind);
    void run(trimmed, password).finally(() => setPending(null));
  };

  const submitForgot = () => {
    if (isBusy || forgotPasswordState === 'sending') return;
    const trimmed = email.trim();
    if (!EMAIL_RE.test(trimmed)) {
      setLocalError('Enter your email above first.');
      return;
    }
    setLocalError(null);
    void onForgotPassword(trimmed);
  };

  const switchMode = (next: EmailMode) => {
    if (isBusy || next === mode) return;
    setMode(next);
    setLocalError(null);
  };

  const shownError =
    localError ?? (error != null ? AppError.from(error).userMessage : null);

  return (
    <div style={STEP_BODY}>
      <div style={CENTER_HERO}>
        <div style={SPARK} aria-hidden>
          <IonIcon icon={sparkles} style={{ fontSize: 40 }} />
        </div>
        <h2 style={HEADING}>Save your progress</h2>
        <p style={SUB}>
          Sign in to keep your streak and pick up right where you left off on any
          device.
        </p>
      </div>

      <div style={{ ...AUTH_GROUP, ...PUSH_DOWN }}>
        <button
          type="button"
          className="riffy-pressable"
          style={authBtnStyle(APPLE_BTN, 'apple', active)}
          onClick={() => runOAuth('apple', onApple)}
          disabled={isBusy}
          aria-busy={active === 'apple'}
        >
          {active === 'apple' ? (
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
          style={authBtnStyle(GOOGLE_BTN, 'google', active)}
          onClick={() => runOAuth('google', onGoogle)}
          disabled={isBusy}
          aria-busy={active === 'google'}
        >
          {active === 'google' ? (
            <IonSpinner name="crescent" />
          ) : (
            <>
              <IonIcon icon={logoGoogle} style={{ fontSize: 20 }} aria-hidden />
              Continue with Google
            </>
          )}
        </button>

        <div style={DIVIDER} aria-hidden>
          <span style={DIVIDER_LINE} />
          or
          <span style={DIVIDER_LINE} />
        </div>

        <div style={SEGMENT} role="tablist" aria-label="Email sign in or sign up">
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'signup'}
            style={segBtnStyle(mode === 'signup')}
            onClick={() => switchMode('signup')}
            disabled={isBusy}
          >
            Sign up
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'login'}
            style={segBtnStyle(mode === 'login')}
            onClick={() => switchMode('login')}
            disabled={isBusy}
          >
            Log in
          </button>
        </div>

        <form style={EMAIL_FORM} onSubmit={submitEmail} noValidate>
          <input
            style={INPUT}
            type="email"
            inputMode="email"
            autoComplete="email"
            placeholder="you@example.com"
            aria-label="Email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (localError) setLocalError(null);
            }}
            disabled={isBusy}
          />
          <input
            style={INPUT}
            type="password"
            autoComplete={mode === 'signup' ? 'new-password' : 'current-password'}
            placeholder="Password"
            aria-label="Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (localError) setLocalError(null);
            }}
            disabled={isBusy}
          />
          <button
            type="submit"
            className="riffy-pressable"
            style={authBtnStyle(SUBMIT_BTN, emailKind, active)}
            disabled={isBusy}
            aria-busy={emailBusy}
          >
            {emailBusy ? (
              <IonSpinner name="crescent" />
            ) : mode === 'signup' ? (
              'Sign up'
            ) : (
              'Log in'
            )}
          </button>
        </form>

        {mode === 'login' && (
          <button
            type="button"
            style={FORGOT_BTN}
            onClick={submitForgot}
            disabled={isBusy || forgotPasswordState === 'sending'}
          >
            {forgotPasswordState === 'sending'
              ? 'Sending…'
              : 'Forgot password?'}
          </button>
        )}

        {forgotPasswordState === 'sent' && (
          <p style={SENT_LINE}>Reset link sent — check your inbox.</p>
        )}

        {shownError != null && <p style={ERROR_LINE}>{shownError}</p>}

        <div style={PRIVACY}>
          <IonIcon icon={lockClosedOutline} aria-hidden />
          We never post anything. Your practice stays yours.
        </div>
      </div>
    </div>
  );
}
