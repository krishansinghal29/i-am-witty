import type { CSSProperties } from 'react';
import { colors, radius } from '@/theme/tokens';
import type { PromptMessage } from '@/types/models';
import { PromptThread, roleTheme } from './prompt_thread';

const ANSWER_CARD: CSSProperties = {
  marginTop: 12,
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: radius.md,
  padding: '12px 14px',
  boxShadow: '0 6px 16px rgba(17, 24, 39, 0.05)',
};

const ANSWER_LABEL: CSSProperties = {
  fontSize: 10,
  fontWeight: 800,
  letterSpacing: 0.8,
  textTransform: 'uppercase',
};

const ANSWER_TEXT: CSSProperties = {
  display: 'block',
  fontSize: 14.5,
  fontWeight: 600,
  color: colors.text,
  lineHeight: 1.55,
  marginTop: 4,
};

export interface ReflectRecapProps {
  promptMessages: PromptMessage[];
  promptLabel?: string;
  userAnswer: string;
}

/** Prompt + submitted answer shown above feedback on the Reflect phase. */
export function ReflectRecap({ promptMessages, promptLabel, userAnswer }: ReflectRecapProps) {
  const you = roleTheme('You');
  const trimmed = userAnswer.trim();
  const isEmpty = !trimmed || trimmed.startsWith('[No response');

  return (
    <div style={{ marginBottom: 16 }}>
      <PromptThread
        messages={promptMessages}
        singleRoleLabel={promptMessages.length === 1 ? promptLabel : undefined}
      />

      <div style={ANSWER_CARD}>
        <span style={{ ...ANSWER_LABEL, color: you.label }}>Your line</span>
        <span
          style={{
            ...ANSWER_TEXT,
            ...(isEmpty
              ? { color: colors.muted, fontStyle: 'italic', fontWeight: 500 }
              : {}),
          }}
        >
          {isEmpty ? 'No response recorded' : trimmed}
        </span>
      </div>
    </div>
  );
}
