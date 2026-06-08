import type { TaskRuntimeViewProps } from '../contract';
import { VoicePromptShell } from '../families/voice_prompt/voice_prompt_shell';
import { PromptThread } from '../families/voice_prompt/prompt_thread';

/** Type 2: a multi-message You/She setup, then one spoken response. */
export function VoiceDialoguePromptV1({ payload, attempt }: TaskRuntimeViewProps) {
  const { prompt } = payload.payload;

  return (
    <VoicePromptShell
      payload={payload}
      attempt={attempt}
      promptArea={<PromptThread messages={prompt.messages} />}
      briefIcon="💬"
    />
  );
}
