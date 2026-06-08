import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { chatbubbleEllipsesOutline, paperPlaneOutline } from 'ionicons/icons';
import { colors } from '@/theme/tokens';
import { useUiStore } from '@/state/stores/ui_store';
import { useAppConfig } from '@/features/config/use_app_config';
import './ui.css';

export interface TopClusterProps {
  /** Overrides the Telegram URL from app config; falls back to config, then hides. */
  telegramUrl?: string;
  /** Source-screen tag passed to the support sheet. */
  supportSource?: string;
}

const CLUSTER: CSSProperties = {
  position: 'fixed',
  top: 'calc(env(safe-area-inset-top, 0px) + 10px)',
  right: 16,
  zIndex: 50,
  display: 'flex',
  alignItems: 'center',
  gap: 10,
};

const BUTTON_BASE: CSSProperties = {
  position: 'relative',
  width: 44,
  height: 44,
  borderRadius: 14,
  border: 'none',
  display: 'grid',
  placeItems: 'center',
  padding: 0,
};

const TG_BUTTON: CSSProperties = {
  ...BUTTON_BASE,
  color: colors.sky,
  background: 'rgba(14, 165, 233, 0.1)',
  boxShadow: '0 6px 16px rgba(14, 165, 233, 0.16)',
  border: '1px solid rgba(14, 165, 233, 0.36)',
};

const CHAT_BUTTON: CSSProperties = {
  ...BUTTON_BASE,
  color: colors.accent,
  background: 'rgba(249, 115, 22, 0.1)',
  boxShadow: '0 6px 16px rgba(249, 115, 22, 0.18)',
  border: '1px solid rgba(249, 115, 22, 0.32)',
};

const DOT: CSSProperties = {
  position: 'absolute',
  top: 7,
  right: 7,
  width: 9,
  height: 9,
  borderRadius: '50%',
  background: colors.red,
  boxShadow: '0 0 0 2px #FFFFFF',
};

/**
 * Persistent top-right cluster: a Telegram community link and a "Chat with us"
 * support bubble (with attention dot). Rendered once by the tab shell.
 */
export function TopCluster({ telegramUrl, supportSource = 'top_cluster' }: TopClusterProps) {
  const attentionDot = useUiStore((state) => state.attentionDot);
  const openSupport = useUiStore((state) => state.openSupport);
  const { values } = useAppConfig();

  const configUrl = values['telegram_community_url'];
  const tgUrl =
    telegramUrl ?? (typeof configUrl === 'string' && configUrl.length > 0 ? configUrl : undefined);

  const openTelegram = () => {
    if (!tgUrl) return;
    window.open(tgUrl, '_blank', 'noopener');
  };

  return (
    <div style={CLUSTER}>
      {tgUrl && (
        <button
          type="button"
          aria-label="Join our Telegram community"
          className="witty-pressable"
          style={TG_BUTTON}
          onClick={openTelegram}
        >
          <IonIcon icon={paperPlaneOutline} style={{ fontSize: 22 }} aria-hidden />
        </button>
      )}

      <button
        type="button"
        aria-label="Chat with us"
        className="witty-pressable"
        style={CHAT_BUTTON}
        onClick={() => openSupport(supportSource)}
      >
        {attentionDot && <span style={DOT} />}
        <IonIcon icon={chatbubbleEllipsesOutline} style={{ fontSize: 22 }} aria-hidden />
      </button>
    </div>
  );
}
