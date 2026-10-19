import { useRef } from 'react';
import type { CSSProperties } from 'react';
import { IonContent, IonPage, useIonViewWillEnter } from '@ionic/react';
import { useHistory } from 'react-router-dom';
import {
  Button,
  Card,
  EmptyView,
  ErrorView,
  LoadingView,
  TopBar,
} from '@/components/ui';
import { colors } from '@/theme/tokens';
import { useRecallToday } from '@/features/recall/use_recall_today';
import type { RecallCardKind } from '@/types/models';
import { CHIP_ROW, STREAK, chipStyle, plural } from './recall_styles';

const HEADER: CSSProperties = {
  padding: 'calc(env(safe-area-inset-top, 0px) + 14px) 20px 0',
};

const TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 27,
  letterSpacing: '-0.5px',
  lineHeight: 1.05,
  color: colors.text,
};

const SUBTITLE: CSSProperties = {
  fontSize: 13,
  color: colors.muted,
  lineHeight: 1.45,
  maxWidth: '30ch',
  marginTop: 5,
};

const DIVIDER: CSSProperties = {
  height: 1,
  background: colors.line,
  margin: '14px 20px 0',
};

const BODY: CSSProperties = {
  padding: '16px 20px 24px',
  display: 'flex',
  flexDirection: 'column',
  gap: 14,
};

const BIG: CSSProperties = { display: 'flex', alignItems: 'baseline', gap: 8 };

const NUM: CSSProperties = {
  fontSize: 52,
  fontWeight: 800,
  letterSpacing: '-2px',
  lineHeight: 1,
  color: colors.text,
  fontVariantNumeric: 'tabular-nums',
};

const UNIT: CSSProperties = { fontSize: 16, fontWeight: 700, color: colors.muted };

const SPLIT: CSSProperties = {
  display: 'flex',
  gap: 14,
  fontSize: 13,
  fontWeight: 600,
  color: colors.muted,
  margin: '8px 0 10px',
};

const SECTION_LABEL: CSSProperties = {
  fontSize: 12,
  fontWeight: 800,
  letterSpacing: '0.6px',
  textTransform: 'uppercase',
  color: colors.muted,
  padding: '0 4px',
};

const ROW: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  fontSize: 14,
  padding: '10px 0',
};

const ROW_TITLE: CSSProperties = {
  flex: 1,
  minWidth: 0,
  fontWeight: 700,
  color: colors.text,
};

const KIND_LABELS: Record<RecallCardKind, [string, string]> = {
  line: ['line', 'lines'],
  concept: ['concept', 'concepts'],
  routine: ['routine', 'routines'],
};

export function RecallPage() {
  const {
    cardCount,
    dueCount,
    newCount,
    kindCounts,
    openCheckins,
    hasWork,
    isLoading,
    isError,
    refetch,
  } = useRecallToday();
  const history = useHistory();

  // Tabs stay mounted, so refetch on each return to pick up progress made on
  // another device. The first enter is skipped: the query is already loading.
  const enteredRef = useRef(false);
  useIonViewWillEnter(() => {
    if (enteredRef.current) void refetch();
    enteredRef.current = true;
  });

  let content;
  if (isLoading) {
    content = <LoadingView message="Loading today’s recall…" centerScreen={false} />;
  } else if (isError) {
    content = (
      <ErrorView
        message="We couldn’t load today’s recall. Give it another try."
        onRetry={() => void refetch()}
      />
    );
  } else if (!hasWork) {
    content = <EmptyView title="Nothing due today" message="Come back tomorrow." />;
  } else {
    const kinds = (Object.keys(KIND_LABELS) as RecallCardKind[]).filter(
      (kind) => kindCounts[kind] > 0,
    );
    content = (
      <>
        {cardCount > 0 && (
          <Card padding={18}>
            <div style={BIG}>
              <span style={NUM}>{cardCount}</span>
              <span style={UNIT}>{cardCount === 1 ? 'card' : 'cards'}</span>
            </div>
            <div style={SPLIT}>
              <span>
                <b style={{ color: colors.text }}>{dueCount}</b> due
              </span>
              <span>
                <b style={{ color: colors.text }}>{newCount}</b> new
              </span>
            </div>
            <div style={CHIP_ROW}>
              {kinds.map((kind) => (
                <span key={kind} style={chipStyle(kind)}>
                  {plural(kindCounts[kind], ...KIND_LABELS[kind])}
                </span>
              ))}
            </div>
          </Card>
        )}

        {openCheckins.length > 0 && (
          <>
            <div style={SECTION_LABEL}>Check-ins first</div>
            <Card padding="4px 16px">
              {openCheckins.map((checkin, i) => (
                <div
                  key={checkin.itemId}
                  style={{ ...ROW, borderTop: i > 0 ? `1px solid ${colors.line}` : 'none' }}
                >
                  <span style={chipStyle('focus')}>Focus</span>
                  <span style={ROW_TITLE}>{checkin.title}</span>
                  {checkin.streak > 0 && (
                    <span style={STREAK}>{plural(checkin.streak, 'day')}</span>
                  )}
                </div>
              ))}
            </Card>
          </>
        )}

        <Button block size="lg" onClick={() => history.push('/recall/session')}>
          Start
        </Button>
      </>
    );
  }

  return (
    <IonPage>
      <IonContent>
        <div style={HEADER}>
          <TopBar supportSource="recall" />
          <h1 style={{ ...TITLE, marginTop: 16 }}>Today’s recall</h1>
          <p style={SUBTITLE}>Say each one out loud before you reveal it.</p>
        </div>
        <div style={DIVIDER} />
        <div style={BODY}>{content}</div>
      </IonContent>
    </IonPage>
  );
}
