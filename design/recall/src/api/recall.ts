import { http } from '@/api/http';
import type {
  Cue,
  CuePatch,
  CueType,
  Draft,
  Item,
  ItemPatch,
  Kind,
  Me,
  NewItemBody,
  Status,
} from '@/api/types';

const q = encodeURIComponent;

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
