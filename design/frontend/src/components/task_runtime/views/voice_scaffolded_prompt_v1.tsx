import type { TaskRuntimeViewProps } from '../contract';
import { VoicePromptShell } from '../families/voice_prompt/voice_prompt_shell';
import { PromptThread } from '../families/voice_prompt/prompt_thread';

/**
 * Type 3: a scenario plus guided Push -> Pull -> Combine rehearsal stages.
 * The shell renders the stepper and runs the multi-take flow; only the final
 * stage is evaluated, though earlier `stageResponses` are still collected/sent.
 */
export function VoiceScaffoldedPromptV1({ payload, attempt }: TaskRuntimeViewProps) {
  const { prompt } = payload.payload;

  return (
    <VoicePromptShell
      payload={payload}
      attempt={attempt}
      scaffolded
      promptArea={
        <PromptThread
          messages={prompt.messages}
          singleRoleLabel={payload.content.promptLabel || undefined}
        />
      }
      briefIcon="🎈"
    />
  );
}
