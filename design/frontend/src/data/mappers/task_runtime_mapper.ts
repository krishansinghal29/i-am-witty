/** Maps task runtime DTOs → view-models. */

import {
  AssignedTechnique,
  Prompt,
  PromptMessage,
  RolePlayOpening,
  Rounds,
  RuntimeContent,
  RuntimePayload,
  TaskRuntime,
  TaskType,
} from '@/types/models';
import {
  ContentDto,
  GeneratedPayloadDto,
  MessageDto,
  PromptDto,
  RolePlayOpeningDto,
  RoundsDto,
  TaskRuntimeDto,
  TaskTypeDto,
  TechniqueDto,
} from '@/data/dto/task_runtime_dto';
import { mapTask } from './catalog_mapper';

/** Read progress, defaulting absent/partial blocks to a single round. */
export function mapRounds(dto: RoundsDto | null | undefined): Rounds {
  return {
    completed: dto?.completed ?? 0,
    total: dto?.total && dto.total > 0 ? dto.total : 1,
  };
}

export function mapTaskType(dto: TaskTypeDto): TaskType {
  return {
    id: dto.id,
    displayName: dto.display_name,
    uiSchemaKey: dto.ui_schema_key,
    runtimeEngineKey: dto.runtime_engine_key,
  };
}

function mapMessage(dto: MessageDto): PromptMessage {
  return {
    role: dto.role,
    content: dto.content,
  };
}

export function mapPrompt(dto: PromptDto): Prompt {
  return {
    messages: dto.messages.map(mapMessage),
    speechText: dto.speech_text,
  };
}

function mapTechnique(dto: TechniqueDto): AssignedTechnique {
  return {
    name: dto.name,
    instruction: dto.instruction,
    example: dto.example,
  };
}

/**
 * Map the optional `content` block with defaults so older/partial responses
 * still render. `recordingLimitSeconds` falls back to the task duration.
 */
function mapContent(
  dto: Partial<ContentDto> | null | undefined,
  fallbackRecordingSeconds: number,
): RuntimeContent {
  const tabs = dto?.feedback_tabs;
  return {
    promptLabel: dto?.prompt_label ?? '',
    responseInstruction: dto?.response_instruction ?? '',
    recordingLimitSeconds: dto?.recording_limit_seconds ?? fallbackRecordingSeconds,
    feedbackTabs: {
      feedbackLabel: tabs?.feedback_label ?? 'Feedback',
      sampleAnswerLabel: tabs?.sample_answer_label ?? 'Better Way',
    },
  };
}

function mapRolePlayOpening(dto: RolePlayOpeningDto): RolePlayOpening {
  return {
    briefHeading: dto.brief_heading,
    narration: dto.narration,
    dialogue: dto.dialogue,
    targetCount: dto.target_count,
    landedCount: dto.landed_count,
    appearance: dto.appearance,
    nextUserMove: dto.next_user_move ?? null,
  };
}

export function mapPayload(dto: GeneratedPayloadDto): RuntimePayload {
  return {
    prompt: mapPrompt(dto.prompt),
    assignedTechnique: dto.assigned_technique != null
      ? mapTechnique(dto.assigned_technique)
      : null,
    audio: {
      audioBase64: dto.audio_base64,
      contentType: dto.audio_content_type,
    },
    avatarImageUrl: dto.avatar_image_url,
    roleplay: dto.roleplay != null ? mapRolePlayOpening(dto.roleplay) : null,
    audioUrl: dto.audio_url ?? null,
    transcript: dto.transcript ?? null,
    captions: (dto.captions ?? []).map((c) => ({
      start: c.start,
      end: c.end,
      text: c.text,
    })),
  };
}

export function mapTaskRuntime(dto: TaskRuntimeDto): TaskRuntime {
  const task = mapTask(dto.task);
  return {
    attemptId: dto.attempt_id,
    task,
    taskType: mapTaskType(dto.task_type),
    content: mapContent(dto.content, task.durationSeconds ?? 30),
    payload: mapPayload(dto.payload),
    rounds: mapRounds(dto.rounds),
  };
}
