/**
 * Maps a task's `uiSchemaKey` to its full runtime view. Adding a task type is
 * one line here (plus the view); the host, route, and data layer never change.
 */

import type { TaskRuntimeView } from './contract';
import { VoiceSinglePromptV1 } from './views/voice_single_prompt_v1';
import { VoiceDialoguePromptV1 } from './views/voice_dialogue_prompt_v1';
import { VoiceScaffoldedPromptV1 } from './views/voice_scaffolded_prompt_v1';

export const taskRuntimeRegistry: Record<string, TaskRuntimeView> = {
  voice_single_prompt_v1: VoiceSinglePromptV1,
  voice_dialogue_prompt_v1: VoiceDialoguePromptV1,
  voice_scaffolded_prompt_v1: VoiceScaffoldedPromptV1,
};
