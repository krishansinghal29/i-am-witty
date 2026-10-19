import { http } from '@/api/http';
import type {
  CheckinResult,
  Cue,
  CuePatch,
  CueType,
  Draft,
  Item,
  ItemPatch,
  Kind,
  Me,
  NewItemBody,
  Outlook,
  SeenResult,
  Session,
  Status,
} from '@/api/types';

const q = encodeURIComponent;

// ---------- public practice ----------

export function getSession(localDate: string): Promise<Session> {
  return http.publicGet(`/v1/recall/session?local_date=${q(localDate)}`);
}

export function markSeen(itemId: string, localDate: string): Promise<SeenResult> {
  return http.publicPost('/v1/recall/seen', { item_id: itemId, local_date: localDate });
}

export function answerCheckin(itemId: string, localDate: string, done: boolean): Promise<CheckinResult> {
  return http.publicPost('/v1/recall/checkins', { item_id: itemId, local_date: localDate, done });
}

export function getOutlook(localDate: string): Promise<Outlook> {
  return http.publicGet(`/v1/recall/outlook?local_date=${q(localDate)}`);
}

// ---------- admin ----------

export function getMe(): Promise<Me> {
  return http.adminGet('/v1/admin/recall/me');
}

export function listCues(): Promise<Cue[]> {
  return http.adminGet('/v1/admin/recall/cues');
}

export function createCue(text: string, type: CueType): Promise<Cue> {
  return http.adminPost('/v1/admin/recall/cues', { text, type });
}

export function updateCue(id: string, patch: CuePatch): Promise<Cue> {
  return http.adminPatch(`/v1/admin/recall/cues/${q(id)}`, patch);
}

/** Moves every line from cue `id` onto `intoCueId` and removes `id`. */
export function mergeCue(id: string, intoCueId: string): Promise<Cue> {
  return http.adminPost(`/v1/admin/recall/cues/${q(id)}/merge`, { into_cue_id: intoCueId });
}

export function listItems(filters: { kind?: Kind; status?: Status } = {}): Promise<Item[]> {
  const params = new URLSearchParams();
  if (filters.kind) params.set('kind', filters.kind);
  if (filters.status) params.set('status', filters.status);
  const query = params.toString();
  return http.adminGet(`/v1/admin/recall/items${query ? `?${query}` : ''}`);
}

export function getItem(id: string): Promise<Item> {
  return http.adminGet(`/v1/admin/recall/items/${q(id)}`);
}

export function createItem(body: NewItemBody): Promise<Item> {
  return http.adminPost('/v1/admin/recall/items', body);
}

export function updateItem(id: string, patch: ItemPatch): Promise<Item> {
  return http.adminPatch(`/v1/admin/recall/items/${q(id)}`, patch);
}

// ---------- admin AI helpers (nothing is saved by these) ----------

export function suggestItem(text: string): Promise<Draft> {
  return http.adminPost('/v1/admin/recall/suggest', { text });
}

export function draftScenarios(body: {
  title: string;
  body: string | null;
  existing: string[];
  count: number;
}): Promise<{ scenarios: string[] }> {
  return http.adminPost('/v1/admin/recall/scenarios', body);
}

export function suggestHint(body: { cue_id: string | null; cue_text: string | null; body: string }): Promise<{ hint: string }> {
  return http.adminPost('/v1/admin/recall/hint', body);
}
