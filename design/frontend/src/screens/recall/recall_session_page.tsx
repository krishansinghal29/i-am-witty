import type { CSSProperties } from 'react';
import { IonContent, IonIcon, IonPage } from '@ionic/react';
import { closeOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import { Button, EmptyView, ErrorView, LoadingView } from '@/components/ui';
import { colors, gradients } from '@/theme/tokens';
import { useRecallSession } from '@/features/recall/use_recall_session';
import { CardView, CheckinView, DoneView } from './session_views';
import { plural } from './recall_styles';

/**
 * Full-screen Recall session: unanswered check-ins, then the day's cards one
 * at a time, then a Done summary. All logic lives in `useRecallSession`.
 */
export function RecallSessionPage() {
  const session = useRecallSession();
  const history = useHistory();

  const close = () => {
    session.leave();
    history.goBack();
  };

  const { step, isDone } = session;
  const progress = session.stepCount > 0 ? session.stepIndex / session.stepCount : 0;

  let progressLabel = '';
  if (step?.type === 'checkin') progressLabel = `Check-in ${step.number} of ${step.total}`;
  if (step?.type === 'card') progressLabel = `${step.number} / ${step.total}`;

  let body;
  let footer = null;
  if (session.isLoading) {
    body = <LoadingView message="Getting today’s cards…" />;
  } else if (session.isError) {
    body = (
      <ErrorView
        message="We couldn’t load today’s recall. Give it another try."
        onRetry={() => void session.refetch()}
      />
    );
  } else if (session.isEmpty) {
    body = <EmptyView title="Nothing due today" message="Come back tomorrow." />;
    footer = (
      <div style={SLOT}>
        <Button block size="lg" variant="ghost" onClick={close}>
          Back to Recall
        </Button>
      </div>
    );
  } else if (isDone) {
    body = (
      <DoneView
        cards={session.answered.cards}
        checkins={session.answered.checkins}
        outlook={session.outlook}
      />
    );
    footer = (
      <div style={SLOT}>
        <Button block size="lg" onClick={close}>
          Back to Recall
        </Button>
      </div>
    );
  } else if (step?.type === 'checkin') {
    body = <CheckinView key={step.checkin.itemId} checkin={step.checkin} />;
    footer = (
      <>
        <div style={SLOT}>
          <Button block size="lg" variant="ghost" onClick={() => session.answerCheckin(false)}>
            No
          </Button>
        </div>
        <div style={SLOT}>
          <Button block size="lg" variant="primary" onClick={() => session.answerCheckin(true)}>
            Yes
          </Button>
        </div>
      </>
    );
  } else if (step?.type === 'card') {
    body = <CardView key={step.card.itemId} card={step.card} revealed={session.revealed} />;
    footer = (
      <div style={SLOT}>
        {session.revealed ? (
          <Button block size="lg" onClick={session.next}>
            Next
          </Button>
        ) : (
          <Button block size="lg" variant="primary" onClick={session.reveal}>
            Reveal
          </Button>
        )}
      </div>
    );
  }

  const showProgress = step !== null && !isDone;

  return (
    <IonPage>
      <IonContent scrollY={false} fullscreen>
        <div style={COL}>
          <header style={HEADER}>
            <button style={ICON_BTN} aria-label="Close" onClick={close}>
              <IonIcon icon={closeOutline} style={{ fontSize: 20 }} />
            </button>
            {showProgress && (
              <>
                <div style={PROG} aria-hidden>
                  <i style={{ ...PROG_FILL, width: `${Math.round(progress * 100)}%` }} />
                </div>
                <span style={COUNT}>{progressLabel}</span>
              </>
            )}
          </header>

          {session.failedCount > 0 && (
            <div style={BANNER} role="status">
              <span style={{ flex: 1 }}>
                Couldn’t save {plural(session.failedCount, 'answer')}. Check your connection.
              </span>
              <button style={BANNER_BTN} onClick={session.retryFailed}>
                Retry
              </button>
            </div>
          )}

          <main style={CONTENT}>{body}</main>
          {footer && <footer style={FOOT}>{footer}</footer>}
        </div>
      </IonContent>
    </IonPage>
  );
}

// ---------------------------------------------------------------------------
// styles
// ---------------------------------------------------------------------------

const COL: CSSProperties = {
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  background: colors.bg,
};

/** Footer buttons grow to share the row (IonButton "block" only fills its parent). */
const SLOT: CSSProperties = { flex: 1, minWidth: 0 };

const HEADER: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  padding: 'calc(env(safe-area-inset-top, 0px) + 8px) 16px 8px',
  minHeight: 56,
};

const ICON_BTN: CSSProperties = {
  width: 40,
  height: 40,
  borderRadius: 13,
  border: `1px solid ${colors.line}`,
  background: colors.surface,
  display: 'grid',
  placeItems: 'center',
  color: colors.muted,
  flex: 'none',
  cursor: 'pointer',
};

const PROG: CSSProperties = {
  flex: 1,
  height: 6,
  borderRadius: 99,
  background: colors.line,
  overflow: 'hidden',
};

const PROG_FILL: CSSProperties = {
  display: 'block',
  height: '100%',
  borderRadius: 99,
  background: gradients.warmCta,
  transition: 'width 0.3s ease',
};

const COUNT: CSSProperties = {
  flex: 'none',
  fontSize: 12,
  fontWeight: 700,
  color: colors.muted,
  fontVariantNumeric: 'tabular-nums',
};

const BANNER: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  margin: '0 16px 4px',
  padding: '10px 12px',
  borderRadius: 12,
  fontSize: 13,
  lineHeight: 1.4,
  color: colors.text,
  background: 'rgba(239, 68, 68, 0.06)',
  border: '1px solid rgba(239, 68, 68, 0.25)',
};

const BANNER_BTN: CSSProperties = {
  flex: 'none',
  border: 'none',
  background: 'transparent',
  color: colors.primary,
  fontWeight: 700,
  fontSize: 13,
  cursor: 'pointer',
};

const CONTENT: CSSProperties = {
  flex: 1,
  minHeight: 0,
  overflowY: 'auto',
  padding: '8px 18px 18px',
  display: 'flex',
  flexDirection: 'column',
};

const FOOT: CSSProperties = {
  flex: 'none',
  display: 'flex',
  gap: 10,
  padding: '10px 18px calc(18px + env(safe-area-inset-bottom, 0px))',
  borderTop: `1px solid ${colors.line}`,
  background: colors.bg,
};
