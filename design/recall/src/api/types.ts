export type CueType = 'reaction' | 'goal';
export type Kind = 'line' | 'concept' | 'routine' | 'focus';
export type Status = 'active' | 'paused' | 'archived';

// ---------- public practice ----------

export interface DayMark {
  date: string;
  done: boolean | null;
}

export interface Checkin {
  item_id: string;
  title: string;
  question: string;
  why: string | null;
  today: boolean | null;
  streak: number;
  last7: DayMark[];
}

export interface LineCard {
  item_id: string;
  kind: 'line';
  is_new: boolean;
  line: {
    cue_text: string;
    cue_type: CueType;
    hint: string | null;
    text: string;
    delivery_note: string | null;
    position: number;
    cue_line_count: number;
  };
}

export interface ConceptCard {
  item_id: string;
  kind: 'concept';
  is_new: boolean;
  concept: {
    name: string;
    definition: string;
    scenario: string;
    scenario_number: number;
    scenario_count: number;
  };
}

export interface RoutineCard {
  item_id: string;
  kind: 'routine';
  is_new: boolean;
  routine: {
    name: string;
    steps: string[];
  };
}

export type Card = LineCard | ConceptCard | RoutineCard;

export interface Session {
  local_date: string;
  checkins: Checkin[];
  cards: Card[];
  counts: {
    due: number;
    new: number;
    line: number;
    concept: number;
    routine: number;
  };
}

export interface SeenResult {
  item_id: string;
  seen_count: number;
  due_on: string;
}

export interface CheckinResult {
  item_id: string;
  done: boolean;
  streak: number;
}

export interface Outlook {
  due_tomorrow: number;
  new_waiting: number;
}

// ---------- admin ----------

export interface Me {
  uid: string;
  email: string | null;
}

export interface Cue {
  id: string;
  text: string;
  type: CueType;
  line_count: number;
}

export interface CueRef {
  id: string;
  text: string;
  type: CueType;
}

export interface Item {
  id: string;
  kind: Kind;
  status: Status;
  cue: CueRef | null;
  hint: string | null;
  title: string | null;
  body: string | null;
  delivery_note: string | null;
  question: string | null;
  steps: string[] | null;
  scenarios: string[] | null;
  source: string | null;
  created_at: string;
  updated_at: string;
}

export type NewItemBody =
  | {
      kind: 'line';
      cue_id: string | null;
      new_cue: { text: string; type: CueType } | null;
      hint: string | null;
      body: string;
      delivery_note: string | null;
      source: string | null;
    }
  | { kind: 'concept'; title: string; body: string; scenarios: string[] }
  | { kind: 'routine'; title: string; steps: string[]; source: string | null }
  | { kind: 'focus'; title: string; question: string; body: string | null };

export interface ItemPatch {
  cue_id?: string;
  hint?: string | null;
  title?: string;
  body?: string | null;
  delivery_note?: string | null;
  question?: string;
  steps?: string[];
  scenarios?: string[];
  source?: string | null;
  status?: Status;
}
