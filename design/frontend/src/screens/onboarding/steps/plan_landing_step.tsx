import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { sparkles } from 'ionicons/icons';
import { colors } from '@/theme/tokens';
import { Button, LoadingView, PlanPath } from '@/components/ui';
import type { PlanNode, PlanNodeStatus } from '@/components/ui';
import { useTodayPlan } from '@/features/home/use_today_plan';
import type { PlanItemView } from '@/features/home/use_today_plan';
import type { PlanItemStatus } from '@/types/models';
import {
  CENTER_HERO,
  PUSH_DOWN,
  STEP_BODY,
} from '@/screens/onboarding/onboarding_styles';

export interface PlanLandingStepProps {
  onEnter: () => void;
}

const SPARK: CSSProperties = {
  width: 84,
  height: 84,
  margin: '10px auto 0',
  borderRadius: 26,
  display: 'grid',
  placeItems: 'center',
  background: 'linear-gradient(150deg, rgba(22, 163, 74, 0.14), rgba(59, 130, 246, 0.12))',
  border: '1px solid #D8E0EA',
  boxShadow: '0 14px 34px rgba(22, 163, 74, 0.16)',
  color: colors.green,
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

function toNodeStatus(status: PlanItemStatus): PlanNodeStatus {
  if (status === 'completed') return 'done';
  if (status === 'current') return 'current';
  return 'upcoming';
}

function toNode(item: PlanItemView): PlanNode {
  return {
    id: item.id,
    status: toNodeStatus(item.status),
    title: item.title,
    highlighted: item.isNextUp,
  };
}

export function PlanLandingStep({ onEnter }: PlanLandingStepProps) {
  const plan = useTodayPlan();

  return (
    <div style={STEP_BODY}>
      <div style={CENTER_HERO}>
        <div style={SPARK} aria-hidden>
          <IonIcon icon={sparkles} style={{ fontSize: 36 }} />
        </div>
        <h2 style={HEADING}>You’re all set 💜</h2>
        <p style={SUB}>
          Day 1 is done — the hardest one. Here’s your plan, ready whenever you are.
        </p>
      </div>

      <div style={{ marginTop: 22 }}>
        {plan.isLoading ? (
          <LoadingView message="Getting your plan ready…" />
        ) : plan.items.length === 0 ? (
          <p style={{ ...SUB, marginTop: 0 }}>
            Fresh practices land here each day — your next one will be waiting.
          </p>
        ) : (
          <PlanPath nodes={plan.items.map(toNode)} />
        )}
      </div>

      <div style={PUSH_DOWN}>
        <Button variant="accent" block onClick={onEnter}>
          See today’s plan
        </Button>
      </div>
    </div>
  );
}
