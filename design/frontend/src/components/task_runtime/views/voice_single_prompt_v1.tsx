import type { CSSProperties } from 'react';
import { colors, radius } from '@/theme/tokens';
import type { RuntimePayload } from '@/types/models';
import type { TaskRuntimeViewProps } from '../contract';
import { VoicePromptShell } from '../families/voice_prompt/voice_prompt_shell';
import { PromptThread } from '../families/voice_prompt/prompt_thread';

const TECHNIQUE_CARD: CSSProperties = {
  marginTop: 12,
  background: 'linear-gradient(155deg, rgba(249, 115, 22, 0.10), #FFFFFF 72%)',
  border: '1px solid rgba(249, 115, 22, 0.3)',
  borderRadius: radius.md,
  padding: '12px 14px',
  textAlign: 'center',
};

/** Type 1: one prompt, one spoken response, optional assigned technique. */
export function VoiceSinglePromptV1({ payload, attempt }: TaskRuntimeViewProps) {
  // Built from the CURRENT rep's runtime so a multi-rep "Next" re-renders the
  // new scenario (prompt + technique), not the one this attempt opened with.
  const renderPrompt = ({ prompt, assignedTechnique }: RuntimePayload) => (
    <>
      <PromptThread messages={prompt.messages} />
      {assignedTechnique && (
        <div style={TECHNIQUE_CARD}>
          <h3 style={{ fontWeight: 800, fontSize: 16, color: colors.accent }}>
            {assignedTechnique.name}
          </h3>
          <p style={{ fontSize: 12.5, color: '#7A5A3A', lineHeight: 1.45, marginTop: 3 }}>
            {assignedTechnique.instruction}
          </p>
          {assignedTechnique.example && (
            <p style={{ fontSize: 12, color: colors.muted, lineHeight: 1.45, marginTop: 6 }}>
              {assignedTechnique.example}
            </p>
          )}
        </div>
      )}
    </>
  );

  return (
    <VoicePromptShell
      payload={payload}
      attempt={attempt}
      renderPrompt={renderPrompt}
      briefIcon="🎭"
    />
  );
}
