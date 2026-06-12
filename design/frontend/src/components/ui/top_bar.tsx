import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import { chatbubbleEllipsesOutline, paperPlaneOutline } from 'ionicons/icons';
import { colors } from '@/theme/tokens';
import { useUiStore } from '@/state/stores/ui_store';
import { useAppConfig } from '@/features/config/use_app_config';
import { useProgressSummary } from '@/features/progress/use_progress_summary';
import { StreakChip } from './streak_chip';
import './ui.css';

export interface TopBarProps {
  /** Overrides the Telegram URL from app config; falls back to config, then hides. */
  telegramUrl?: string;
  /** Source-screen tag passed to the support sheet. */
  supportSource?: string;
}

const ROW: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  gap: 10,
};

const ACTIONS: CSSProperties = {
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
 * Inline page top bar: the streak chip on the left, a Telegram community link
 * and a "Chat with us" support bubble (with attention dot) on the right.
 * Rendered at the top of each tab page (Home, Practice, Role play) for one
 * consistent header. The streak is read from the shared `/v1/home` query, so it
 * stays in sync with the home screen without an extra fetch.
 */
export function TopBar({ telegramUrl, supportSource = 'top_bar' }: TopBarProps) {
  const attentionDot = useUiStore((state) => state.attentionDot);
  const openSupport = useUiStore((state) => state.openSupport);
  const { values } = useAppConfig();
  const { currentStreak } = useProgressSummary();

  const configUrl = values['telegram_community_url'];
  const tgUrl =
    telegramUrl ?? (typeof configUrl === 'string' && configUrl.length > 0 ? configUrl : undefined);

  const openTelegram = () => {
    if (!tgUrl) return;
    window.open(tgUrl, '_blank', 'noopener');
  };

  return (
    <div style={ROW}>
      <StreakChip count={currentStreak} />

      <div style={ACTIONS}>
        {tgUrl && (
          <button
            type="button"
            aria-label="Join our Telegram community"
            className="riffy-pressable"
            style={TG_BUTTON}
            onClick={openTelegram}
          >
            <IonIcon icon={paperPlaneOutline} style={{ fontSize: 22 }} aria-hidden />
          </button>
        )}

        <button
          type="button"
          aria-label="Chat with us"
          className="riffy-pressable"
          style={CHAT_BUTTON}
          onClick={() => openSupport(supportSource)}
        >
          {attentionDot && <span style={DOT} />}
          <IonIcon icon={chatbubbleEllipsesOutline} style={{ fontSize: 22 }} aria-hidden />
        </button>
      </div>
    </div>
  );
}
