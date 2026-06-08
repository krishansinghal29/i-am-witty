import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { flame, ribbonOutline, sparkles } from 'ionicons/icons';
import { colors } from '@/theme/tokens';
import { Button, Celebration } from '@/components/ui';
import {
  CENTER_HERO,
  PUSH_DOWN,
  STEP_BODY,
} from '@/screens/onboarding/onboarding_styles';

export interface VariableRewardStepProps {
  onContinue: () => void;
}

const BADGE: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 8,
  alignSelf: 'center',
  fontWeight: 700,
  fontSize: 12.5,
  color: '#B45309',
  background: 'rgba(245, 163, 10, 0.12)',
  border: '1px solid rgba(245, 163, 10, 0.4)',
  padding: '7px 14px',
  borderRadius: 999,
  boxShadow: '0 8px 18px rgba(245, 163, 10, 0.16)',
};

const FLAME: CSSProperties = {
  position: 'relative',
  width: 96,
  height: 96,
  margin: '22px auto 0',
  borderRadius: 30,
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
  marginTop: 28,
};

const SUB: CSSProperties = {
  fontSize: 14,
  color: colors.muted,
  lineHeight: 1.5,
  maxWidth: '30ch',
  margin: '10px auto 0',
};

const INSIGHT: CSSProperties = {
  display: 'flex',
  gap: 11,
  marginTop: 22,
  borderRadius: 12,
  background: 'rgba(14, 165, 233, 0.08)',
  border: '1px solid rgba(14, 165, 233, 0.28)',
  padding: '13px 14px',
  textAlign: 'left',
};

export function VariableRewardStep({ onContinue }: VariableRewardStepProps) {
  return (
    <div style={STEP_BODY}>
      <Celebration show label="Day 1 — unlocked" />

      <div style={CENTER_HERO}>
        <span style={BADGE}>
          <IonIcon icon={ribbonOutline} aria-hidden />
          First step — unlocked
        </span>

        <div style={FLAME} aria-hidden>
          <IonIcon icon={flame} style={{ fontSize: 44, color: colors.accent }} />
          <span style={DAY_PILL}>Day 1</span>
        </div>

        <h2 style={HEADING}>You actually did it. 🔥</h2>
        <p style={SUB}>
          That’s the hardest rep — the first one. You just proved you can do this
          in private, no pressure.
        </p>
      </div>

      <div style={INSIGHT}>
        <IonIcon
          icon={sparkles}
          style={{ color: colors.sky, fontSize: 18, flex: 'none', marginTop: 1 }}
          aria-hidden
        />
        <p style={{ fontSize: 13, lineHeight: 1.5, color: colors.text }}>
          Keep showing up for tiny reps like this and the quick, warm version
          starts to feel like the natural one.
        </p>
      </div>

      <div style={PUSH_DOWN}>
        <Button variant="accent" block onClick={onContinue}>
          Keep going
        </Button>
      </div>
    </div>
  );
}
