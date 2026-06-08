import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import {
  lockClosedOutline,
  sparklesOutline,
  timeOutline,
} from 'ionicons/icons';
import { colors, radius, shadows } from '@/theme/tokens';
import { Button } from '@/components/ui';
import { triggerByValue } from '@/screens/onboarding/triggers';
import {
  KICKER,
  PRIVACY,
  PUSH_DOWN,
  QUESTION,
  STEP_BODY,
  SUBTITLE,
} from '@/screens/onboarding/onboarding_styles';

export interface TinyPracticeStepProps {
  trigger: string | null;
  ready: boolean;
  onStart: () => void;
}

const TUNED: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 7,
  alignSelf: 'flex-start',
  fontSize: 11.5,
  fontWeight: 600,
  color: colors.active,
  background: 'rgba(59, 130, 246, 0.10)',
  border: '1px solid rgba(59, 130, 246, 0.34)',
  padding: '6px 11px',
  borderRadius: 999,
  marginBottom: 14,
};

const CARD: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 13,
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: radius.md,
  boxShadow: shadows.soft,
  padding: 15,
};

const THUMB: CSSProperties = {
  width: 56,
  height: 56,
  borderRadius: 17,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  fontSize: 27,
  background: 'rgba(249, 115, 22, 0.12)',
  border: '1px solid rgba(249, 115, 22, 0.22)',
};

const META: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 7,
  marginTop: 5,
  fontSize: 12,
  color: colors.muted,
  fontWeight: 500,
};

const PROMPT: CSSProperties = {
  marginTop: 16,
  borderRadius: radius.md,
  border: '1px dashed #D8E0EA',
  background: colors.tint,
  padding: 15,
};

const PROMPT_LABEL: CSSProperties = {
  fontSize: 11,
  letterSpacing: '0.8px',
  textTransform: 'uppercase',
  color: colors.faint,
  fontWeight: 700,
};

const PROMPT_BODY: CSSProperties = {
  fontWeight: 600,
  fontSize: 16,
  lineHeight: 1.45,
  marginTop: 7,
  color: colors.text,
};

export function TinyPracticeStep({ trigger, ready, onStart }: TinyPracticeStepProps) {
  const option = triggerByValue(trigger);

  return (
    <div style={STEP_BODY}>
      <span style={KICKER}>Your first tiny win</span>
      <h1 style={QUESTION}>One line is plenty.</h1>
      <p style={SUBTITLE}>
        Text-first and low pressure. React however feels natural — there are no
        wrong answers, and you can speak it out loud later if you’d rather.
      </p>

      <div style={{ marginTop: 22 }}>
        <span style={TUNED}>
          <IonIcon icon={sparklesOutline} aria-hidden />
          Tuned for {option?.forPhrase ?? 'you'}
        </span>

        <div style={CARD}>
          <div style={THUMB} aria-hidden>
            {option?.emoji ?? '🎭'}
          </div>
          <div>
            <h3 style={{ fontWeight: 700, fontSize: 18, letterSpacing: '-0.2px', color: colors.text }}>
              A quick warm-up
            </h3>
            <div style={META}>
              <IonIcon icon={timeOutline} aria-hidden />
              <span>About a minute</span>
              <span aria-hidden>·</span>
              <span>Just you</span>
            </div>
          </div>
        </div>

        <div style={PROMPT}>
          <div style={PROMPT_LABEL}>What happens next</div>
          <div style={PROMPT_BODY}>
            We’ll hand you one tiny scenario. Say or type a single line — then we’ll
            show you a warmer, sharper way.
          </div>
        </div>

        <div style={PRIVACY}>
          <IonIcon icon={lockClosedOutline} aria-hidden />
          Private — no one’s listening. This is just practice.
        </div>
      </div>

      <div style={PUSH_DOWN}>
        <Button variant="accent" block onClick={onStart} disabled={!ready}>
          {ready ? 'Start my tiny win' : 'Getting it ready…'}
        </Button>
      </div>
    </div>
  );
}
