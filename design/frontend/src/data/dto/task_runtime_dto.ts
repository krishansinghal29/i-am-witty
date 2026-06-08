/** Wire shapes for task runtime endpoints (snake_case). */

import { TaskDto } from './catalog_dto';

export interface TaskTypeDto {
  id: string;
  display_name: string;
  ui_schema_key: string;
  runtime_engine_key: string;
}

export interface MessageDto {
  role: string;
  content: string;
}

export interface PromptDto {
  messages: MessageDto[];
  speech_text: string | null;
}

export interface TechniqueDto {
  name: string;
  instruction: string;
  example: string;
}

export interface GeneratedPayloadDto {
  prompt: PromptDto;
  assigned_technique: TechniqueDto | null;
  scaffold_stages: Record<string, unknown>[];
  audio_base64: string | null;
  audio_content_type: string | null;
  avatar_image_url: string | null;
}

export interface FeedbackTabsDto {
  feedback_label: string;
  sample_answer_label: string;
}

export interface ContentDto {
  prompt_label: string;
  response_instruction: string;
  recording_limit_seconds: number;
  feedback_tabs: FeedbackTabsDto;
}

export interface TaskRuntimeDto {
  attempt_id: string;
  task: TaskDto;
  task_type: TaskTypeDto;
  /** Optional for backward compatibility with older/partial responses. */
  content?: Partial<ContentDto> | null;
  payload: GeneratedPayloadDto;
}

// ---------------------------------------------------------------------------
// Request bodies
// ---------------------------------------------------------------------------

export interface RuntimeStartRequestDto {
  source: string;
  daily_plan_item_id?: string | null;
}
