import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';
import { Capacitor } from '@capacitor/core';
import { IonIcon } from '@ionic/react';
import {
  closeOutline,
  infinite,
  libraryOutline,
  micOutline,
  sparkles,
} from 'ionicons/icons';
import { Button, LoadingView, Sheet } from '@/components/ui';
import { colors } from '@/theme/tokens';
import { useUiStore } from '@/state/stores/ui_store';
import { useAppConfig } from '@/features/config/use_app_config';
import { usePaywall } from '@/features/entitlement/use_paywall';
import { AppError } from '@/data/errors/app_error';
import type { SubscriptionPackage } from '@/integrations/ports/subscription_gateway';

const CONTAINER: CSSProperties = {
  position: 'relative',
  padding: '6px 22px calc(env(safe-area-inset-bottom, 0px) + 24px)',
  overflowY: 'auto',
  maxHeight: '100%',
};

const CLOSE_BTN: CSSProperties = {
  position: 'absolute',
  top: 6,
  right: 14,
  width: 30,
  height: 30,
  borderRadius: '50%',
  border: `1px solid ${colors.line}`,
  background: colors.tint,
  color: colors.muted,
  display: 'grid',
  placeItems: 'center',
  cursor: 'pointer',
  zIndex: 2,
};

const BANNER: CSSProperties = {
  margin: '8px 0 16px',
  textAlign: 'center',
  fontSize: 12.5,
  fontWeight: 600,
  color: '#B45309',
  background: 'rgba(245, 163, 10, 0.12)',
  border: '1px solid rgba(245, 163, 10, 0.4)',
  padding: '9px 12px',
  borderRadius: 12,
};

const HERO: CSSProperties = { textAlign: 'center' };

const SPARK: CSSProperties = {
  width: 58,
  height: 58,
  margin: '0 auto 12px',
  borderRadius: 18,
  display: 'grid',
  placeItems: 'center',
  color: colors.accent,
  background: 'rgba(249, 115, 22, 0.14)',
  border: '1px solid rgba(249, 115, 22, 0.3)',
  boxShadow: '0 12px 24px rgba(249, 115, 22, 0.2)',
};

const HERO_TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 23,
  letterSpacing: '-0.3px',
  color: colors.text,
};

const HERO_SUB: CSSProperties = {
  fontSize: 13,
  color: colors.muted,
  lineHeight: 1.5,
  maxWidth: '32ch',
  margin: '7px auto 0',
};

const FEATS: CSSProperties = {
  listStyle: 'none',
  margin: '18px 4px 0',
  padding: 0,
  display: 'flex',
  flexDirection: 'column',
  gap: 11,
};

const FEAT_ITEM: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  fontSize: 13.5,
  fontWeight: 500,
  color: colors.text,
};

const FEAT_ICON: CSSProperties = {
  width: 30,
  height: 30,
  borderRadius: 9,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  color: colors.accent,
  background: colors.tint,
  border: `1px solid ${colors.line}`,
};

const PLANS: CSSProperties = {
  marginTop: 22,
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 11,
};

const DOWNLOAD: CSSProperties = {
  marginTop: 22,
  display: 'flex',
  flexDirection: 'column',
  gap: 10,
};

const TRIAL: CSSProperties = {
  textAlign: 'center',
  fontSize: 12,
  color: colors.muted,
  fontWeight: 600,
  margin: '15px 0 11px',
};

const ERROR_LINE: CSSProperties = {
  textAlign: 'center',
  fontSize: 12.5,
  color: colors.red,
  fontWeight: 600,
  marginTop: 10,
};

const FINE: CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  gap: 10,
  marginTop: 14,
  fontSize: 12,
  color: colors.faint,
  fontWeight: 600,
};

const FINE_LINK: CSSProperties = { cursor: 'pointer', color: colors.muted };

const LATER: CSSProperties = {
  display: 'block',
  width: '100%',
  textAlign: 'center',
  marginTop: 14,
  padding: 6,
  fontSize: 13,
  fontWeight: 600,
  color: colors.muted,
  background: 'transparent',
  border: 'none',
  cursor: 'pointer',
};

const FEATURES: { icon: string; label: string }[] = [
  { icon: infinite, label: 'Unlimited practice, every day' },
  { icon: micOutline, label: 'Deeper feedback on every take' },
  { icon: libraryOutline, label: 'The full library + Role play (soon)' },
];

function bannerText(reason: string | null): string {
  switch (reason) {
    case 'catalog_locked':
      return 'That exercise is part of Riffy+';
    case 'free_limit_reached':
      return 'That’s your free practices for today — your streak’s safe';
    default:
      return 'Go further with Riffy+';
  }
}

function periodLabel(pkg: SubscriptionPackage): string {
  if (pkg.period === 'annual') return 'Annual';
  if (pkg.period === 'monthly') return 'Monthly';
  return pkg.title || 'Plan';
}

function periodSuffix(pkg: SubscriptionPackage): string {
  if (pkg.period === 'annual') return '/yr';
  if (pkg.period === 'monthly') return '/mo';
  return '';
}

const PLAN_ORDER: Record<SubscriptionPackage['period'], number> = {
  annual: 0,
  monthly: 1,
  unknown: 2,
};

interface PlanCardProps {
  pkg: SubscriptionPackage;
  selected: boolean;
  best: boolean;
  onSelect: () => void;
}

function PlanCard({ pkg, selected, best, onSelect }: PlanCardProps) {
  const style: CSSProperties = {
    position: 'relative',
    textAlign: 'left',
    borderRadius: 12,
    padding: '15px 14px 13px',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    gap: 3,
    background: selected
      ? 'linear-gradient(160deg, rgba(59, 130, 246, 0.1), #FFFFFF)'
      : colors.surface,
    border: `1px solid ${selected ? colors.primary : colors.line}`,
    boxShadow: selected
      ? 'inset 0 0 0 1px rgba(59,130,246,0.6), 0 10px 22px rgba(59, 130, 246, 0.18)'
      : 'none',
  };

  return (
    <button type="button" style={style} onClick={onSelect} aria-pressed={selected}>
      {best && (
        <span
          style={{
            position: 'absolute',
            top: -9,
            left: '50%',
            transform: 'translateX(-50%)',
            whiteSpace: 'nowrap',
            fontSize: 9,
            fontWeight: 800,
            letterSpacing: '0.5px',
            color: '#FFFFFF',
            background: colors.accent,
            padding: '3px 9px',
            borderRadius: 6,
            textTransform: 'uppercase',
          }}
        >
          Best value
        </span>
      )}
      <span style={{ fontWeight: 600, fontSize: 13.5, color: colors.muted }}>
        {periodLabel(pkg)}
      </span>
      <span style={{ fontWeight: 700, fontSize: 20, letterSpacing: '-0.3px', color: colors.text }}>
        {pkg.priceString}
        <small style={{ fontSize: 12, color: colors.muted, fontWeight: 500 }}>
          {periodSuffix(pkg)}
        </small>
      </span>
    </button>
  );
}

export function PaywallSheet() {
  const paywallOpen = useUiStore((state) => state.paywallOpen);
  const paywallReason = useUiStore((state) => state.paywallReason);
  const closePaywall = useUiStore((state) => state.closePaywall);

  const { values } = useAppConfig();
  // In-app purchases run natively (StoreKit/Play Billing). On the web there is
  // no checkout — we point users to download the app — so the paywall renders a
  // store-download CTA there and skips loading offerings.
  const isNative = Capacitor.isNativePlatform();
  const {
    packages,
    isLoading,
    isEmpty,
    purchase,
    restore,
    isPurchasing,
    isRestoring,
    purchaseError,
  } = usePaywall({ enabled: paywallOpen && isNative });

  const [selectedId, setSelectedId] = useState<string | null>(null);

  const ordered = useMemo(
    () => [...packages].sort((a, b) => PLAN_ORDER[a.period] - PLAN_ORDER[b.period]),
    [packages],
  );

  // Pre-select the annual plan (best value) once offerings load.
  useEffect(() => {
    if (selectedId == null && ordered.length > 0) {
      const annual = ordered.find((p) => p.period === 'annual');
      setSelectedId((annual ?? ordered[0]).identifier);
    }
  }, [ordered, selectedId]);

  const selected = ordered.find((p) => p.identifier === selectedId) ?? null;

  const handleDismiss = () => {
    setSelectedId(null);
    closePaywall();
  };

  const handlePurchase = async () => {
    if (!selected) return;
    try {
      await purchase(selected);
      handleDismiss();
    } catch {
      // Surfaced inline via purchaseError; keep the sheet open to retry.
    }
  };

  const handleRestore = async () => {
    try {
      await restore();
      handleDismiss();
    } catch {
      // No-op: restore failures keep the sheet open.
    }
  };

  const configUrl = (key: string): string | null => {
    const v = values[key];
    return typeof v === 'string' && v.length > 0 ? v : null;
  };

  const openUrl = (key: string) => {
    const url = configUrl(key);
    if (url) window.open(url, '_blank', 'noopener');
  };

  const iosUrl = configUrl('ios_app_store_url');
  const androidUrl = configUrl('android_play_store_url');

  const busy = isPurchasing || isRestoring;

  return (
    <Sheet isOpen={paywallOpen} onDidDismiss={handleDismiss}>
      <div style={CONTAINER}>
        <button
          type="button"
          aria-label="Close"
          style={CLOSE_BTN}
          onClick={handleDismiss}
        >
          <IonIcon icon={closeOutline} style={{ fontSize: 16 }} aria-hidden />
        </button>

        <div style={BANNER}>{bannerText(paywallReason)}</div>

        <div style={HERO}>
          <div style={SPARK}>
            <IonIcon icon={sparkles} style={{ fontSize: 28 }} aria-hidden />
          </div>
          <h2 style={HERO_TITLE}>Keep the momentum going</h2>
          <p style={HERO_SUB}>
            Come back free tomorrow — or go unlimited right now with Riffy+.
          </p>
        </div>

        <ul style={FEATS}>
          {FEATURES.map((feat) => (
            <li key={feat.label} style={FEAT_ITEM}>
              <span style={FEAT_ICON}>
                <IonIcon icon={feat.icon} style={{ fontSize: 15 }} aria-hidden />
              </span>
              {feat.label}
            </li>
          ))}
        </ul>

        {!isNative ? (
          <div style={DOWNLOAD}>
            <p style={{ ...HERO_SUB, margin: '22px auto 6px' }}>
              Riffy+ is purchased in the app. Download Riffy to subscribe, then
              sign in here to unlock it everywhere.
            </p>
            {iosUrl && (
              <Button
                variant="accent"
                block
                onClick={() => openUrl('ios_app_store_url')}
              >
                Download on the App Store
              </Button>
            )}
            {androidUrl && (
              <Button
                variant={iosUrl ? 'ghost' : 'accent'}
                block
                onClick={() => openUrl('android_play_store_url')}
              >
                Get it on Google Play
              </Button>
            )}
            {!iosUrl && !androidUrl && (
              <p style={{ ...HERO_SUB, marginTop: 4 }}>
                The app is coming soon — hang tight.
              </p>
            )}
          </div>
        ) : isLoading ? (
          <LoadingView message="Loading plans…" />
        ) : isEmpty ? (
          <p style={{ ...HERO_SUB, marginTop: 22 }}>
            Plans aren’t available right now. You can keep practicing free, and try
            again later.
          </p>
        ) : (
          <>
            <div style={PLANS}>
              {ordered.map((pkg) => (
                <PlanCard
                  key={pkg.identifier}
                  pkg={pkg}
                  selected={pkg.identifier === selectedId}
                  best={pkg.period === 'annual'}
                  onSelect={() => setSelectedId(pkg.identifier)}
                />
              ))}
            </div>

            <p style={TRIAL}>
              {selected
                ? `${selected.priceString}${periodSuffix(selected)} · cancel anytime`
                : 'Cancel anytime'}
            </p>

            <Button
              variant="accent"
              block
              onClick={handlePurchase}
              loading={isPurchasing}
              disabled={busy || !selected}
            >
              Subscribe
            </Button>

            {purchaseError != null && (
              <p style={ERROR_LINE}>{AppError.from(purchaseError).userMessage}</p>
            )}
          </>
        )}

        <div style={FINE}>
          {isNative && (
            <>
              <span
                style={FINE_LINK}
                role="button"
                tabIndex={0}
                onClick={handleRestore}
              >
                {isRestoring ? 'Restoring…' : 'Restore'}
              </span>
              <span aria-hidden>·</span>
            </>
          )}
          <span style={FINE_LINK} role="button" tabIndex={0} onClick={() => openUrl('terms_url')}>
            Terms
          </span>
          <span aria-hidden>·</span>
          <span style={FINE_LINK} role="button" tabIndex={0} onClick={() => openUrl('privacy_url')}>
            Privacy
          </span>
        </div>

        <button type="button" style={LATER} onClick={handleDismiss} disabled={busy}>
          Maybe later
        </button>
      </div>
    </Sheet>
  );
}
