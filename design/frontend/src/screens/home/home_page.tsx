import type { CSSProperties } from 'react';
import { IonContent, IonPage } from '@ionic/react';
import {
  EmptyView,
  ErrorView,
  LoadingView,
  PlanPath,
  TopBar,
  WeekStrip,
} from '@/components/ui';
import type { PlanNode, PlanNodeStatus } from '@/components/ui';
import { colors } from '@/theme/tokens';
import { useTodayPlan } from '@/features/home/use_today_plan';
import type { PlanItemView } from '@/features/home/use_today_plan';
import { useProgressSummary } from '@/features/progress/use_progress_summary';
import type { PlanItemStatus } from '@/types/models';

const HEADER: CSSProperties = {
  padding: 'calc(env(safe-area-inset-top, 0px) + 14px) 20px 0',
};

const HELLO: CSSProperties = { fontSize: 14, color: colors.muted, fontWeight: 600 };

const TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 28,
  letterSpacing: '-0.5px',
  lineHeight: 1.05,
  color: colors.text,
  marginTop: 4,
};

const SUBTITLE: CSSProperties = {
  fontSize: 13.5,
  color: colors.muted,
  lineHeight: 1.45,
  maxWidth: '32ch',
  marginTop: 7,
};

const DIVIDER: CSSProperties = {
  height: 1,
  background: colors.line,
  margin: '16px 20px 0',
};

const BODY: CSSProperties = { padding: '4px 20px 24px' };

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

export function HomePage() {
  const plan = useTodayPlan();
  const progress = useProgressSummary();

  const isLoading = plan.isLoading || progress.isLoading;
  const isError = plan.isError || progress.isError;

  const handleRetry = () => {
    void plan.refetch();
    void progress.refetch();
  };

  const onSelect = (id: string) => {
    const item = plan.items.find((i) => i.id === id);
    if (item) plan.openTask(item);
  };

  let content;
  if (isLoading) {
    content = <LoadingView message="Getting today’s plan ready…" />;
  } else if (isError) {
    content = (
      <ErrorView
        message="We couldn’t load your plan just now. Give it another try."
        onRetry={handleRetry}
      />
    );
  } else {
    content = (
      <>
        <div style={HEADER}>
          <TopBar supportSource="home" />

          <div style={{ marginTop: 16 }}>
            <WeekStrip days={progress.week} />
          </div>
        </div>

        <div style={DIVIDER} />

        <div style={BODY}>
          <p style={HELLO}>Hey, you</p>
          <h1 style={TITLE}>Today’s plan</h1>
          <p style={SUBTITLE}>
            A few tiny wins. No pressure — just pick up where you left off.
          </p>

          <div style={{ marginTop: 14 }}>
            {plan.items.length === 0 ? (
              <EmptyView
                title="Your plan is taking shape"
                message="Fresh practices land here each day. Check back in a moment."
              />
            ) : (
              <PlanPath nodes={plan.items.map(toNode)} onSelect={onSelect} />
            )}
          </div>
        </div>
      </>
    );
  }

  return (
    <IonPage>
      <IonContent>{content}</IonContent>
    </IonPage>
  );
}
