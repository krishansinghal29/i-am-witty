import type { CSSProperties, ReactNode } from 'react';
import { IonContent, IonIcon, IonPage } from '@ionic/react';
import {
  barbellOutline,
  checkmarkCircle,
  chevronForwardOutline,
  documentTextOutline,
  logOutOutline,
  paperPlaneOutline,
  personOutline,
  shieldCheckmarkOutline,
  sparkles,
} from 'ionicons/icons';
import {
  Button,
  ErrorView,
  LoadingView,
  StreakChip,
} from '@/components/ui';
import { colors, radius } from '@/theme/tokens';
import { useProgressSummary } from '@/features/progress/use_progress_summary';
import { useEntitlement } from '@/features/entitlement/use_entitlement';
import { useAppConfig } from '@/features/config/use_app_config';
import { useProfile } from '@/features/profile/use_profile';
import { useUiStore } from '@/state/stores/ui_store';

const HEADER: CSSProperties = {
  padding: 'calc(env(safe-area-inset-top, 0px) + 14px) 20px 12px',
};

const PAGE_TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 29,
  lineHeight: 1.05,
  letterSpacing: '-0.5px',
  color: colors.text,
};

const DIVIDER: CSSProperties = {
  height: 1,
  background: colors.line,
  margin: '0 20px',
};

const BODY: CSSProperties = { padding: '16px 20px calc(env(safe-area-inset-bottom, 0px) + 24px)' };

const HERO: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 15,
};

const AVATAR: CSSProperties = {
  width: 72,
  height: 72,
  borderRadius: 24,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  color: colors.primary,
  background: 'rgba(59, 130, 246, 0.12)',
  border: '1px solid rgba(59, 130, 246, 0.3)',
  boxShadow: '0 10px 24px rgba(59, 130, 246, 0.18)',
};

const HERO_NAME: CSSProperties = {
  fontWeight: 700,
  fontSize: 23,
  letterSpacing: '-0.3px',
  color: colors.text,
};

const HERO_SUB: CSSProperties = {
  fontSize: 13,
  color: colors.muted,
  lineHeight: 1.4,
  marginTop: 3,
};

const STATS: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 10,
  marginTop: 18,
};

const STAT_CARD: CSSProperties = {
  borderRadius: radius.md,
  padding: '16px 8px',
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  textAlign: 'center',
  boxShadow: '0 6px 16px rgba(17, 24, 39, 0.05)',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: 8,
};

const STAT_NUM: CSSProperties = {
  fontWeight: 700,
  fontSize: 22,
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  gap: 6,
  color: colors.green,
};

const STAT_LABEL: CSSProperties = {
  fontSize: 10,
  color: colors.muted,
  fontWeight: 700,
  letterSpacing: '0.3px',
  textTransform: 'uppercase',
};

const UPSELL: CSSProperties = {
  marginTop: 16,
  borderRadius: radius.md,
  padding: '15px 16px',
  display: 'flex',
  alignItems: 'center',
  gap: 13,
  background:
    'linear-gradient(135deg, rgba(249, 115, 22, 0.12), rgba(59, 130, 246, 0.1) 72%)',
  border: '1px solid rgba(249, 115, 22, 0.36)',
  boxShadow: '0 12px 26px rgba(249, 115, 22, 0.14)',
};

const UPSELL_ICON: CSSProperties = {
  width: 50,
  height: 50,
  borderRadius: 16,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  color: colors.accent,
  background: 'rgba(249, 115, 22, 0.14)',
  border: '1px solid rgba(249, 115, 22, 0.3)',
};

const UPSELL_TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 16.5,
  letterSpacing: '-0.2px',
  color: colors.text,
};

const UPSELL_SUB: CSSProperties = {
  fontSize: 12,
  color: colors.muted,
  marginTop: 3,
  lineHeight: 1.35,
};

const ACTIVE_CARD: CSSProperties = {
  marginTop: 16,
  borderRadius: radius.md,
  padding: '15px 16px',
  display: 'flex',
  alignItems: 'center',
  gap: 13,
  background: colors.surface,
  border: '1px solid rgba(22, 163, 74, 0.32)',
  boxShadow: '0 6px 18px rgba(17, 24, 39, 0.06)',
};

const ACTIVE_ICON: CSSProperties = {
  width: 50,
  height: 50,
  borderRadius: 16,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  color: colors.green,
  background: 'rgba(22, 163, 74, 0.12)',
  border: '1px solid rgba(22, 163, 74, 0.3)',
};

const MENU: CSSProperties = {
  marginTop: 16,
  borderRadius: radius.md,
  overflow: 'hidden',
  border: `1px solid ${colors.line}`,
  background: colors.surface,
  boxShadow: '0 6px 18px rgba(17, 24, 39, 0.06)',
};

const MENU_ICON: CSSProperties = {
  width: 38,
  height: 38,
  borderRadius: 12,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  color: colors.muted,
  background: colors.tint,
  border: `1px solid ${colors.line}`,
};

const MENU_LABEL: CSSProperties = {
  flex: 1,
  fontWeight: 600,
  fontSize: 14.5,
  color: colors.text,
};

const PILL: CSSProperties = {
  fontWeight: 700,
  fontSize: 11,
  color: colors.sky,
  background: 'rgba(14, 165, 233, 0.12)',
  border: '1px solid rgba(14, 165, 233, 0.36)',
  padding: '4px 10px',
  borderRadius: 999,
};

const SIGNOUT: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 7,
  width: '100%',
  margin: '18px 0 0',
  padding: 8,
  fontSize: 13,
  fontWeight: 600,
  color: colors.faint,
  background: 'transparent',
  border: 'none',
  cursor: 'pointer',
};

function asUrl(value: unknown): string | undefined {
  return typeof value === 'string' && value.length > 0 ? value : undefined;
}

interface MenuRowProps {
  icon: string;
  iconTint?: { color: string; background: string; border: string };
  label: string;
  trailing?: ReactNode;
  last?: boolean;
  onClick: () => void;
}

function MenuRow({ icon, iconTint, label, trailing, last, onClick }: MenuRowProps) {
  const row: CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: 13,
    padding: '14px 15px',
    cursor: 'pointer',
    borderBottom: last ? 'none' : `1px solid ${colors.line}`,
    background: 'transparent',
    width: '100%',
    textAlign: 'left',
  };
  const iconStyle: CSSProperties = iconTint
    ? { ...MENU_ICON, color: iconTint.color, background: iconTint.background, border: `1px solid ${iconTint.border}` }
    : MENU_ICON;

  return (
    <button type="button" className="witty-pressable" style={row} onClick={onClick}>
      <span style={iconStyle}>
        <IonIcon icon={icon} style={{ fontSize: 18 }} aria-hidden />
      </span>
      <span style={MENU_LABEL}>{label}</span>
      {trailing ?? (
        <IonIcon
          icon={chevronForwardOutline}
          style={{ fontSize: 16, color: colors.faint }}
          aria-hidden
        />
      )}
    </button>
  );
}

export function ProfilePage() {
  const progress = useProgressSummary();
  const entitlement = useEntitlement();
  const { values } = useAppConfig();
  const { isAuthenticated, signOut, isSigningOut } = useProfile();
  const openPaywall = useUiStore((state) => state.openPaywall);
  const openSupport = useUiStore((state) => state.openSupport);

  const telegramUrl = asUrl(values['telegram_community_url']);
  const termsUrl = asUrl(values['terms_url']);
  const privacyUrl = asUrl(values['privacy_url']);

  const isLoading = progress.isLoading || entitlement.isLoading;
  const isError = progress.isError || entitlement.isError;

  const handleRetry = () => {
    void progress.refetch();
    void entitlement.refetch();
  };

  const openExternal = (url?: string) => {
    if (url) window.open(url, '_blank', 'noopener');
  };

  let content: ReactNode;
  if (isLoading) {
    content = <LoadingView message="Loading your profile…" />;
  } else if (isError) {
    content = (
      <ErrorView
        message="We couldn’t load your profile just now. Give it another try."
        onRetry={handleRetry}
      />
    );
  } else {
    content = (
      <div style={BODY}>
        <div style={HERO}>
          <div style={AVATAR}>
            <IonIcon icon={personOutline} style={{ fontSize: 34 }} aria-hidden />
          </div>
          <div>
            <div style={HERO_NAME}>Hey there</div>
            <div style={HERO_SUB}>Progress vs. your past self — never others.</div>
          </div>
        </div>

        <div style={STATS}>
          <div style={STAT_CARD}>
            <StreakChip count={progress.currentStreak} />
            <span style={STAT_LABEL}>Day streak</span>
          </div>
          <div style={STAT_CARD}>
            <span style={STAT_NUM}>
              <IonIcon icon={barbellOutline} style={{ fontSize: 20 }} aria-hidden />
              {progress.completedCount}
            </span>
            <span style={STAT_LABEL}>Exercises</span>
          </div>
        </div>

        {entitlement.isWittyPlus ? (
          <div style={ACTIVE_CARD}>
            <div style={ACTIVE_ICON}>
              <IonIcon icon={checkmarkCircle} style={{ fontSize: 26 }} aria-hidden />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={UPSELL_TITLE}>Witty+ is active</div>
              <p style={UPSELL_SUB}>You’ve got the full library and unlimited practice.</p>
            </div>
          </div>
        ) : (
          <div style={UPSELL}>
            <div style={UPSELL_ICON}>
              <IonIcon icon={sparkles} style={{ fontSize: 24 }} aria-hidden />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={UPSELL_TITLE}>Go unlimited with Witty+</div>
              <p style={UPSELL_SUB}>Unlimited practice, deeper feedback &amp; more.</p>
            </div>
            <Button variant="accent" size="sm" onClick={() => openPaywall('profile')}>
              Upgrade
            </Button>
          </div>
        )}

        <div style={MENU}>
          {telegramUrl && (
            <MenuRow
              icon={paperPlaneOutline}
              iconTint={{
                color: colors.sky,
                background: 'rgba(14, 165, 233, 0.1)',
                border: 'rgba(14, 165, 233, 0.36)',
              }}
              label="Join our Telegram community"
              trailing={<span style={PILL}>Join</span>}
              onClick={() => openExternal(telegramUrl)}
            />
          )}
          <MenuRow
            icon={sparkles}
            iconTint={{
              color: colors.accent,
              background: 'rgba(249, 115, 22, 0.1)',
              border: 'rgba(249, 115, 22, 0.32)',
            }}
            label="Chat with us"
            onClick={() => openSupport('profile')}
          />
          {termsUrl && (
            <MenuRow
              icon={documentTextOutline}
              label="Terms of Service"
              onClick={() => openExternal(termsUrl)}
            />
          )}
          {privacyUrl && (
            <MenuRow
              icon={shieldCheckmarkOutline}
              label="Privacy Policy"
              last
              onClick={() => openExternal(privacyUrl)}
            />
          )}
        </div>

        {isAuthenticated && (
          <button
            type="button"
            className="witty-pressable"
            style={SIGNOUT}
            onClick={() => void signOut()}
            disabled={isSigningOut}
          >
            <IonIcon icon={logOutOutline} style={{ fontSize: 16 }} aria-hidden />
            {isSigningOut ? 'Signing out…' : 'Sign out'}
          </button>
        )}
      </div>
    );
  }

  return (
    <IonPage>
      <IonContent>
        <div style={HEADER}>
          <h1 style={PAGE_TITLE}>Profile</h1>
        </div>
        <div style={DIVIDER} />
        {content}
      </IonContent>
    </IonPage>
  );
}
