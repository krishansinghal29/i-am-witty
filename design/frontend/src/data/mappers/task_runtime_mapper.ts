/** Maps task runtime DTOs → view-models. */

import {
  AssignedTechnique,
  Prompt,
  PromptMessage,
  RuntimePayload,
  ScaffoldStage,
  TaskRuntime,
  TaskType,
} from '@/types/models';
import {
  GeneratedPayloadDto,
  MessageDto,
  PromptDto,
  TaskRuntimeDto,
  TaskTypeDto,
  TechniqueDto,
} from '@/data/dto/task_runtime_dto';
import { mapTask } from './catalog_mapper';

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

function mapScaffoldStage(raw: Record<string, unknown>): ScaffoldStage {
  // Extract known fields; spread the rest to satisfy the index signature.
  const {
    position,
    label,
    title,
    instruction,
    is_final_submission,
    ...rest
  } = raw;

  return {
    position: typeof position === 'number' ? position : 0,
    label: typeof label === 'string' ? label : '',
    title: typeof title === 'string' ? title : '',
    instruction: typeof instruction === 'string' ? instruction : '',
    isFinalSubmission: typeof is_final_submission === 'boolean' ? is_final_submission : false,
    ...rest,
  };
}

function mapPayload(dto: GeneratedPayloadDto): RuntimePayload {
  return {
    prompt: mapPrompt(dto.prompt),
    assignedTechnique: dto.assigned_technique != null
      ? mapTechnique(dto.assigned_technique)
      : null,
    scaffoldStages: dto.scaffold_stages.map(mapScaffoldStage),
    audio: {
      audioBase64: dto.audio_base64,
      contentType: dto.audio_content_type,
    },
    avatarImageUrl: dto.avatar_image_url,
  };
}

export function mapTaskRuntime(dto: TaskRuntimeDto): TaskRuntime {
  return {
    attemptId: dto.attempt_id,
    task: mapTask(dto.task),
    taskType: mapTaskType(dto.task_type),
    payload: mapPayload(dto.payload),
  };
}
