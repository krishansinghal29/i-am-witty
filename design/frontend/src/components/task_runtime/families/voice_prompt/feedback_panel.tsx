import { useEffect, useState } from 'react';
import type { CSSProperties } from 'react';
import { sparklesOutline, chatbubbleEllipsesOutline } from 'ionicons/icons';
import { IonIcon } from '@ionic/react';
import { colors, gradients, radius } from '@/theme/tokens';
import { Celebration, useReducedMotion } from '@/components/ui';
import type { EvaluationResult, FeedbackTabs } from '@/types/models';

export interface FeedbackPanelProps {
  evaluation: EvaluationResult;
  feedbackTabs: FeedbackTabs;
}

type Tab = 'feedback' | 'sample';

const SCOREHEAD: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 13,
  background: 'linear-gradient(150deg, rgba(22, 163, 74, 0.12), #FFFFFF 60%)',
  border: '1px solid rgba(22, 163, 74, 0.3)',
  borderRadius: 18,
  padding: '14px 16px',
  boxShadow: '0 8px 22px rgba(22, 163, 74, 0.10)',
};

const KICKER: CSSProperties = {
  fontSize: 10.5,
  fontWeight: 800,
  letterSpacing: 1,
  textTransform: 'uppercase',
  color: colors.green,
};

const TABS: CSSProperties = { display: 'flex', gap: 8, marginTop: 16 };

function tabStyle(active: boolean): CSSProperties {
  return {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 7,
    padding: 11,
    borderRadius: 13,
    border: `1.5px solid ${active ? 'transparent' : colors.line}`,
    background: active ? gradients.activeTab : colors.surface,
    color: active ? '#FFFFFF' : colors.muted,
    fontSize: 13,
    fontWeight: 700,
    cursor: 'pointer',
    boxShadow: active ? '0 8px 18px rgba(59, 130, 246, 0.3)' : 'none',
  };
}

const HTML_PANE: CSSProperties = {
  marginTop: 14,
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: radius.md,
  padding: '14px 16px',
  fontSize: 13.5,
  lineHeight: 1.6,
  color: colors.muted,
  boxShadow: '0 5px 14px rgba(17, 24, 39, 0.04)',
};

const SAMPLE_PANE: CSSProperties = {
  ...HTML_PANE,
  background: 'linear-gradient(150deg, rgba(249, 115, 22, 0.08), #FFFFFF 70%)',
  border: '1px solid rgba(249, 115, 22, 0.22)',
  color: colors.text,
  fontWeight: 600,
};

/**
 * The Reflect-phase feedback. Renders the backend's TRUSTED evaluation HTML
 * (four-part feedback + alternative answers) via `dangerouslySetInnerHTML`,
 * isolated to this panel, and fires a one-time Celebration on first reveal.
 */
export function FeedbackPanel({ evaluation, feedbackTabs }: FeedbackPanelProps) {
  const [tab, setTab] = useState<Tab>('feedback');
  const [celebrate, setCelebrate] = useState(true);
  const reduced = useReducedMotion();

  useEffect(() => {
    const ms = reduced ? 1600 : 3000;
    const timer = setTimeout(() => setCelebrate(false), ms);
    return () => clearTimeout(timer);
  }, [reduced]);

  return (
    <div className="witty-rise">
      <Celebration show={celebrate} label={evaluation.styleLabel ?? undefined} />

      <div style={SCOREHEAD}>
        <div
          style={{
            width: 46,
            height: 46,
            borderRadius: 14,
            flex: 'none',
            display: 'grid',
            placeItems: 'center',
            fontSize: 24,
            background: colors.surface,
            border: '1px solid rgba(22, 163, 74, 0.25)',
          }}
          aria-hidden
        >
          <IonIcon icon={sparklesOutline} style={{ color: colors.green, fontSize: 24 }} />
        </div>
        <div>
          <div style={KICKER}>Nice — that landed</div>
          <h2
            style={{
              fontWeight: 800,
              fontSize: 19,
              letterSpacing: '-0.3px',
              marginTop: 2,
              color: colors.text,
            }}
          >
            {evaluation.styleLabel ?? 'Feedback ready'}
          </h2>
        </div>
      </div>

      <div style={TABS} role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === 'feedback'}
          style={tabStyle(tab === 'feedback')}
          onClick={() => setTab('feedback')}
        >
          <IonIcon icon={chatbubbleEllipsesOutline} aria-hidden />
          {feedbackTabs.feedbackLabel}
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === 'sample'}
          style={tabStyle(tab === 'sample')}
          onClick={() => setTab('sample')}
        >
          <IonIcon icon={sparklesOutline} aria-hidden />
          {feedbackTabs.sampleAnswerLabel}
        </button>
      </div>

      {tab === 'feedback' ? (
        <div
          style={HTML_PANE}
          // Backend-generated, trusted evaluation HTML — isolated to this panel.
          dangerouslySetInnerHTML={{ __html: evaluation.feedbackHtml }}
        />
      ) : (
        <div
          style={SAMPLE_PANE}
          dangerouslySetInnerHTML={{ __html: evaluation.sampleAnswerHtml }}
        />
      )}
    </div>
  );
}
