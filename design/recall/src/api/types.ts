export type CueType = 'reaction' | 'goal';
export type Kind = 'line' | 'concept' | 'routine' | 'focus';
export type Status = 'active' | 'paused' | 'archived';

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

/** What the AI drafted from Quick add text. Nothing is saved yet. */
export interface DraftCue {
  /** Null when the AI proposes a new cue. */
  id: string | null;
  text: string;
  type: CueType;
  line_count: number;
}

export interface Draft {
  kind: Kind;
  cue: DraftCue | null;
  hint: string | null;
  /** Suggested hint for the cue's single existing line that has none. */
  sibling_hint: { item_id: string; body: string; hint: string } | null;
  title: string | null;
  body: string | null;
  delivery_note: string | null;
  question: string | null;
  steps: string[] | null;
  scenarios: string[] | null;
}

export interface CuePatch {
  text?: string;
  type?: CueType;
}

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
