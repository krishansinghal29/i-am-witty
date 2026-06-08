import type { CSSProperties, ReactNode } from 'react';
import { IonIcon, IonSpinner } from '@ionic/react';
import { alertCircleOutline, sparklesOutline } from 'ionicons/icons';
import { colors } from '@/theme/tokens';
import { Button } from './button';

const CONTAINER: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 14,
  padding: '48px 24px',
  textAlign: 'center',
  minHeight: 220,
};

const TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 18,
  color: colors.text,
};

const MESSAGE: CSSProperties = {
  fontSize: 14,
  lineHeight: 1.5,
  color: colors.muted,
  maxWidth: '34ch',
};

function iconBubble(tint: string): CSSProperties {
  return {
    width: 56,
    height: 56,
    borderRadius: '50%',
    display: 'grid',
    placeItems: 'center',
    background: `${tint}1F`,
    color: tint,
  };
}

export interface LoadingViewProps {
  message?: string;
}

export function LoadingView({ message = 'Loading…' }: LoadingViewProps) {
  return (
    <div style={CONTAINER} aria-busy="true">
      <IonSpinner name="crescent" style={{ color: colors.accent, width: 36, height: 36 }} />
      <p style={MESSAGE}>{message}</p>
    </div>
  );
}

export interface EmptyViewProps {
  title?: string;
  message?: string;
  /** ionicons icon name; defaults to a gentle sparkles glyph. */
  icon?: string;
  action?: ReactNode;
}

export function EmptyView({
  title = 'Nothing here yet',
  message = 'This space will fill in as you go.',
  icon = sparklesOutline,
  action,
}: EmptyViewProps) {
  return (
    <div style={CONTAINER}>
      <div style={iconBubble(colors.accent)}>
        <IonIcon icon={icon} style={{ fontSize: 26 }} aria-hidden />
      </div>
      <h2 style={TITLE}>{title}</h2>
      <p style={MESSAGE}>{message}</p>
      {action}
    </div>
  );
}

export interface ErrorViewProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  retryLabel?: string;
}

export function ErrorView({
  title = 'Something went wrong',
  message = 'We couldn’t load this just now. Give it another try.',
  onRetry,
  retryLabel = 'Try again',
}: ErrorViewProps) {
  return (
    <div style={CONTAINER} role="alert">
      <div style={iconBubble(colors.red)}>
        <IonIcon icon={alertCircleOutline} style={{ fontSize: 26 }} aria-hidden />
      </div>
      <h2 style={TITLE}>{title}</h2>
      <p style={MESSAGE}>{message}</p>
      {onRetry && (
        <Button variant="ghost" size="sm" onClick={onRetry}>
          {retryLabel}
        </Button>
      )}
    </div>
  );
}
