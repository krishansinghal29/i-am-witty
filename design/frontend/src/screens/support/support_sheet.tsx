import { useEffect, useState } from 'react';
import type { CSSProperties } from 'react';
import { IonIcon } from '@ionic/react';
import {
  checkmarkOutline,
  closeOutline,
  lockClosedOutline,
} from 'ionicons/icons';
import { Button, Sheet } from '@/components/ui';
import { colors, radius } from '@/theme/tokens';
import { useUiStore } from '@/state/stores/ui_store';
import { useSupport } from '@/features/support/use_support';
import { AppError } from '@/data/errors/app_error';

const CONTAINER: CSSProperties = {
  position: 'relative',
  padding: '6px 22px calc(env(safe-area-inset-bottom, 0px) + 28px)',
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

const TITLE: CSSProperties = {
  fontWeight: 700,
  fontSize: 21,
  lineHeight: 1.15,
  letterSpacing: '-0.3px',
  color: colors.text,
  marginTop: 6,
  paddingRight: 34,
};

const SUB: CSSProperties = {
  fontSize: 13.5,
  color: colors.muted,
  lineHeight: 1.5,
  marginTop: 8,
};

const TEXTAREA: CSSProperties = {
  width: '100%',
  marginTop: 16,
  minHeight: 116,
  resize: 'none',
  borderRadius: radius.md,
  border: `1px solid ${colors.line}`,
  background: colors.tint,
  color: colors.text,
  padding: '13px 14px',
  fontFamily: 'inherit',
  fontSize: 14,
  lineHeight: 1.5,
  outline: 'none',
};

const ERROR_LINE: CSSProperties = {
  fontSize: 12.5,
  color: colors.red,
  fontWeight: 600,
  marginTop: 10,
};

const TAG: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 7,
  fontSize: 11.5,
  color: colors.faint,
  fontWeight: 600,
  marginTop: 16,
};

const SUCCESS_WRAP: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  textAlign: 'center',
  gap: 12,
  padding: '22px 6px 6px',
};

const SUCCESS_BADGE: CSSProperties = {
  width: 64,
  height: 64,
  borderRadius: 22,
  display: 'grid',
  placeItems: 'center',
  color: colors.green,
  background: 'rgba(22, 163, 74, 0.12)',
  border: '1px solid rgba(22, 163, 74, 0.3)',
};

export function SupportSheet() {
  const supportOpen = useUiStore((state) => state.supportOpen);
  const sourceScreen = useUiStore((state) => state.supportSourceScreen);
  const closeSupport = useUiStore((state) => state.closeSupport);
  const setAttentionDot = useUiStore((state) => state.setAttentionDot);

  const { submit, isSubmitting, isSuccess, error, reset } = useSupport();
  const [message, setMessage] = useState('');

  // Once the message lands, the "chat with us" nudge has served its purpose.
  useEffect(() => {
    if (isSuccess) setAttentionDot(false);
  }, [isSuccess, setAttentionDot]);

  const trimmed = message.trim();
  const canSend = trimmed.length > 0 && !isSubmitting;

  const handleSend = async () => {
    if (!canSend) return;
    try {
      await submit({ messageText: trimmed, sourceScreen });
    } catch {
      // Surfaced inline via `error`; keep the sheet open so they can retry.
    }
  };

  const handleDismiss = () => {
    closeSupport();
    setMessage('');
    reset();
  };

  return (
    <Sheet isOpen={supportOpen} onDidDismiss={handleDismiss}>
      <div style={CONTAINER}>
        <button
          type="button"
          aria-label="Close"
          style={CLOSE_BTN}
          onClick={handleDismiss}
        >
          <IonIcon icon={closeOutline} style={{ fontSize: 16 }} aria-hidden />
        </button>

        {isSuccess ? (
          <div style={SUCCESS_WRAP}>
            <div style={SUCCESS_BADGE}>
              <IonIcon icon={checkmarkOutline} style={{ fontSize: 30 }} aria-hidden />
            </div>
            <h2 style={{ ...TITLE, paddingRight: 0, marginTop: 0 }}>
              Thanks — got it!
            </h2>
            <p style={{ ...SUB, marginTop: 0, maxWidth: '32ch' }}>
              A real human reads every message. We’ll take it from here.
            </p>
            <div style={{ width: '100%', marginTop: 8 }}>
              <Button variant="accent" block onClick={handleDismiss}>
                Done
              </Button>
            </div>
          </div>
        ) : (
          <>
            <h2 style={TITLE}>Got an idea, or did something break?</h2>
            <p style={SUB}>
              Tell us anything — a bug, a half-baked idea, or just a hi. A real
              human reads every single message.
            </p>

            <textarea
              style={TEXTAREA}
              placeholder="Type away…"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={isSubmitting}
              aria-label="Your message"
            />

            {error != null && (
              <p style={ERROR_LINE}>{AppError.from(error).userMessage}</p>
            )}

            <div style={{ marginTop: 14 }}>
              <Button
                variant="accent"
                block
                onClick={handleSend}
                loading={isSubmitting}
                disabled={!canSend}
              >
                Send it our way
              </Button>
            </div>

            <div style={TAG}>
              <IonIcon icon={lockClosedOutline} style={{ fontSize: 13 }} aria-hidden />
              Private · always here, on every screen
            </div>
          </>
        )}
      </div>
    </Sheet>
  );
}
