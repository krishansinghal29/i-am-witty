import type { CSSProperties } from 'react';
import { IonContent, IonPage } from '@ionic/react';
import { lockClosedOutline } from 'ionicons/icons';
import { EmptyView, TopBar } from '@/components/ui';
import { colors } from '@/theme/tokens';

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
  maxWidth: '28ch',
  marginTop: 5,
};

const DIVIDER: CSSProperties = {
  height: 1,
  background: colors.line,
  margin: '14px 20px 0',
};

const BODY: CSSProperties = { padding: '14px 20px 24px' };

/**
 * Role play tab. A locked placeholder for now — live, in-character roleplay
 * conversations unlock once the user has practised enough. Shares the same
 * header (streak + Telegram + chat) and theme as Home and Practice.
 */
export function RoleplayPage() {
  return (
    <IonPage>
      <IonContent>
        <div style={HEADER}>
          <TopBar supportSource="roleplay" />
          <h1 style={{ ...TITLE, marginTop: 16 }}>Role play</h1>
          <p style={SUBTITLE}>
            Live, in-character conversations to put your wit to the test.
          </p>
        </div>
        <div style={DIVIDER} />
        <div style={BODY}>
          <EmptyView
            icon={lockClosedOutline}
            title="Roleplay is locked"
            message="Practice more to unlock roleplay."
          />
        </div>
      </IonContent>
    </IonPage>
  );
}
