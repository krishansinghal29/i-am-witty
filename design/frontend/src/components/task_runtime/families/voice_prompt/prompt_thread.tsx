import type { CSSProperties } from 'react';
import { colors, radius } from '@/theme/tokens';
import type { PromptMessage, PromptRole } from '@/types/models';

const ROSE = '#FB7185';

interface RoleTheme {
  /** Avatar background. */
  avatar: string;
  /** Role-label colour. */
  label: string;
  /** Single uppercase initial for the avatar. */
  initial: string;
}

/** `She` reads rosy/coral, `You` reads blue; others fall back to muted. */
export function roleTheme(role: PromptRole): RoleTheme {
  switch (role) {
    case 'She':
      return { avatar: `linear-gradient(140deg, ${ROSE}, ${colors.accent})`, label: ROSE, initial: 'S' };
    case 'You':
      return { avatar: colors.primary, label: colors.primary, initial: 'Y' };
    case 'Topic':
      return { avatar: colors.sky, label: colors.sky, initial: 'T' };
    case 'Storyteller':
      return { avatar: colors.amber, label: colors.amber, initial: 'S' };
    default:
      return { avatar: colors.muted, label: colors.muted, initial: (role[0] ?? '?').toUpperCase() };
  }
}

const CARD: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 11,
  background: colors.surface,
  border: `1px solid ${colors.line}`,
  borderRadius: radius.md,
  padding: '11px 13px',
  boxShadow: '0 5px 14px rgba(17, 24, 39, 0.05)',
};

const AVATAR: CSSProperties = {
  width: 30,
  height: 30,
  borderRadius: 10,
  flex: 'none',
  display: 'grid',
  placeItems: 'center',
  color: '#FFFFFF',
  fontWeight: 800,
  fontSize: 12,
};

const ROLE_LABEL: CSSProperties = {
  fontSize: 10,
  fontWeight: 800,
  letterSpacing: 0.8,
  textTransform: 'uppercase',
};

const CONTENT: CSSProperties = {
  display: 'block',
  fontSize: 13.5,
  fontWeight: 600,
  color: colors.text,
  lineHeight: 1.35,
  marginTop: 1,
};

export interface PromptMessageRowProps {
  message: PromptMessage;
  /** Override the visible role label (defaults to the message role). */
  roleLabel?: string;
}

export function PromptMessageRow({ message, roleLabel }: PromptMessageRowProps) {
  const theme = roleTheme(message.role);
  return (
    <div style={CARD}>
      <span style={{ ...AVATAR, background: theme.avatar }} aria-hidden>
        {theme.initial}
      </span>
      <span style={{ flex: 1, minWidth: 0 }}>
        <span style={{ ...ROLE_LABEL, color: theme.label }}>
          {roleLabel ?? message.role}
        </span>
        <span style={CONTENT}>{message.content}</span>
      </span>
    </div>
  );
}

export interface PromptThreadProps {
  messages: PromptMessage[];
  /** Override the role label for the single-message case (e.g. "Scenario"). */
  singleRoleLabel?: string;
}

/** Renders prompt messages as role-chipped cards (single card or a thread). */
export function PromptThread({ messages, singleRoleLabel }: PromptThreadProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
      {messages.map((message, i) => (
        <PromptMessageRow
          key={`${message.role}-${i}`}
          message={message}
          roleLabel={
            messages.length === 1 && singleRoleLabel != null
              ? singleRoleLabel
              : undefined
          }
        />
      ))}
    </div>
  );
}
