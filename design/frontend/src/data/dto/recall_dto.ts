/** Wire shapes for the Recall practice endpoints (snake_case). */

export interface RecallCheckinDayDto {
  date: string;
  done: boolean | null;
}

export interface RecallCheckinDto {
  item_id: string;
  title: string;
  question: string;
  why: string | null;
  today: boolean | null;
  streak: number;
  last7: RecallCheckinDayDto[];
}

export interface RecallLineDto {
  cue_text: string;
  cue_type: string;
  hint: string | null;
  text: string;
  delivery_note: string | null;
  position: number;
  cue_line_count: number;
}

export interface RecallConceptDto {
  name: string;
  definition: string;
  scenario: string;
  scenario_number: number;
  scenario_count: number;
}

export interface RecallRoutineDto {
  name: string;
  steps: string[];
}

export interface RecallCardDto {
  item_id: string;
  kind: string;
  is_new: boolean;
  line: RecallLineDto | null;
  concept: RecallConceptDto | null;
  routine: RecallRoutineDto | null;
}

export interface RecallCountsDto {
  due: number;
  new: number;
  line: number;
  concept: number;
  routine: number;
}

export interface RecallSessionDto {
  local_date: string;
  checkins: RecallCheckinDto[];
  cards: RecallCardDto[];
  counts: RecallCountsDto;
}

export interface RecallOutlookDto {
  due_tomorrow: number;
  new_waiting: number;
}

export interface RecallSeenDto {
  item_id: string;
  seen_count: number;
  due_on: string;
}

export interface RecallCheckinResultDto {
  item_id: string;
  done: boolean;
  streak: number;
}

// ---------------------------------------------------------------------------
// Request bodies
// ---------------------------------------------------------------------------

export interface RecallSeenRequestDto {
  item_id: string;
  local_date: string;
}

export interface RecallCheckinRequestDto {
  item_id: string;
  local_date: string;
  done: boolean;
}
