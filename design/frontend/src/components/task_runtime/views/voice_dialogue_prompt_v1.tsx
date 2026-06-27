import type { TaskRuntimeViewProps } from '../contract';
import { VoicePromptShell } from '../families/voice_prompt/voice_prompt_shell';
import { PromptThread } from '../families/voice_prompt/prompt_thread';

/** Type 2: a multi-message You/She setup, then one spoken response. */
export function VoiceDialoguePromptV1({ payload, attempt }: TaskRuntimeViewProps) {
  return (
    <VoicePromptShell
      payload={payload}
      attempt={attempt}
      renderPrompt={(runtime) => <PromptThread messages={runtime.prompt.messages} />}
      briefIcon="💬"
    />
  );
}
