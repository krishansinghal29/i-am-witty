/**
 * The item form's state, validation, save path and fields, shared by the full
 * form (New / Edit item) and Quick add's editable draft, so both save the
 * same way: a lone hintless sibling gets its hint PATCHed first, then the item
 * is created or updated.
 */

import { useCallback, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { createCue, createItem, draftScenarios, suggestHint, updateItem } from '@/api/recall';
import { ApiError, errorMessage } from '@/api/http';
import type { Audience, Cue, CueType, Draft, Item, Kind } from '@/api/types';
import { CheckIcon, CloseIcon, DownIcon, LockIcon, PlusIcon, SparkleIcon, UpIcon } from '@/components/Icons';
import { CueCombobox } from './CueCombobox';

export const KINDS: { key: Kind; label: string; noun: string }[] = [
  { key: 'line', label: 'Line', noun: 'line' },
  { key: 'concept', label: 'Concept', noun: 'concept' },
  { key: 'routine', label: 'Routine', noun: 'routine' },
  { key: 'focus', label: 'Focus', noun: 'focus' },
];

export function parseKind(value: string | null): Kind {
  return KINDS.some((k) => k.key === value) ? (value as Kind) : 'line';
}

export function noun(kind: Kind) {
  return KINDS.find((k) => k.key === kind)?.noun ?? 'item';
}

/** Focus check-ins are personal, so they default to the admin only. */
export function defaultAudience(kind: Kind): Audience {
  return kind === 'focus' ? 'admin' : 'everyone';
}

function quote(text: string) {
  return `“${text}”`;
}

const norm = (s: string | null | undefined) => (s ?? '').trim().toLowerCase();
const orNull = (s: string) => (s.trim() ? s.trim() : null);

type FieldKey =
  | 'cue'
  | 'hint'
  | 'siblingHint'
  | 'lineText'
  | 'title'
  | 'definition'
  | 'question'
  | 'steps'
  | 'scenarios';

type Errors = Partial<Record<FieldKey, string>>;

export interface Form {
  kind: Kind;
  cueType: CueType;
  cueText: string;
  cueId: string | null;
  hint: string;
  siblingHint: string;
  lineText: string;
  deliveryNote: string;
  source: string;
  title: string;
  definition: string;
  scenarios: string[];
  steps: string[];
  question: string;
  why: string;
  audience: Audience;
  /** Once the admin picks an audience, switching kind stops resetting it to the kind's default. */
  audienceTouched: boolean;
}

/** Form fields the AI can fill; the cue's three fields count as one ("cueText"). */
type SuggestKey = Exclude<keyof Form, 'kind' | 'cueType' | 'cueId' | 'audience' | 'audienceTouched'>;

export function emptyForm(kind: Kind): Form {
  return {
    kind,
    cueType: 'reaction',
    cueText: '',
    cueId: null,
    hint: '',
    siblingHint: '',
    lineText: '',
    deliveryNote: '',
    source: '',
    title: '',
    definition: '',
    scenarios: [''],
    steps: [''],
    question: '',
    why: '',
    audience: defaultAudience(kind),
    audienceTouched: false,
  };
}

export function formFromItem(item: Item): Form {
  const form = emptyForm(item.kind);
  return {
    ...form,
    cueType: item.cue?.type ?? 'reaction',
    cueText: item.cue?.text ?? '',
    cueId: item.cue?.id ?? null,
    hint: item.hint ?? '',
    lineText: item.kind === 'line' ? item.body ?? '' : '',
    deliveryNote: item.delivery_note ?? '',
    source: item.source ?? '',
    title: item.title ?? '',
    definition: item.kind === 'concept' ? item.body ?? '' : '',
    scenarios: item.scenarios && item.scenarios.length > 0 ? item.scenarios : [''],
    steps: item.steps && item.steps.length > 0 ? item.steps : [''],
    question: item.question ?? '',
    why: item.kind === 'focus' ? item.body ?? '' : '',
    audience: item.audience ?? defaultAudience(item.kind),
    audienceTouched: true,
  };
}

export function formFromDraft(draft: Draft): Form {
  const form = emptyForm(draft.kind);
  const body = draft.body ?? '';
  return {
    ...form,
    cueType: draft.cue?.type ?? 'reaction',
    cueText: draft.cue?.text ?? '',
    cueId: draft.cue?.id ?? null,
    hint: draft.hint ?? '',
    siblingHint: draft.sibling_hint?.hint ?? '',
    lineText: draft.kind === 'line' ? body : '',
    deliveryNote: draft.delivery_note ?? '',
    title: draft.title ?? '',
    definition: draft.kind === 'concept' ? body : '',
    scenarios: draft.scenarios && draft.scenarios.length > 0 ? draft.scenarios : [''],
    steps: draft.steps && draft.steps.length > 0 ? draft.steps : [''],
    question: draft.question ?? '',
    why: draft.kind === 'focus' ? body : '',
  };
}

/** Which fields of a fresh draft came from the AI (non-empty ones). */
export function suggestedKeys(form: Form): SuggestKey[] {
  const keys: SuggestKey[] = [];
  const text: SuggestKey[] = ['cueText', 'hint', 'siblingHint', 'lineText', 'deliveryNote', 'title', 'definition', 'question', 'why'];
  for (const key of text) if ((form[key] as string).trim()) keys.push(key);
  if (form.scenarios.some((s) => s.trim())) keys.push('scenarios');
  if (form.steps.some((s) => s.trim())) keys.push('steps');
  return keys;
}

/** Changing kind keeps the main text: a line, a definition and a focus "why" carry over to an empty slot. */
export function switchKind(form: Form, kind: Kind): Partial<Form> {
  const main = form.kind === 'line' ? form.lineText : form.kind === 'concept' ? form.definition : form.kind === 'focus' ? form.why : '';
  const patch: Partial<Form> = { kind };
  if (!form.audienceTouched) patch.audience = defaultAudience(kind);
  if (main.trim()) {
    if (kind === 'line' && !form.lineText.trim()) patch.lineText = main;
    if (kind === 'concept' && !form.definition.trim()) patch.definition = main;
    if (kind === 'focus' && !form.why.trim()) patch.why = main;
  }
  return patch;
}

/** Backend 422 reasons mapped onto the field they belong to. */
const REASON_FIELD: Record<string, FieldKey> = {
  line_requires_one_cue: 'cue',
  hint_required: 'hint',
  hint_duplicate: 'hint',
  sibling_hint_missing: 'siblingHint',
  title_required: 'title',
  question_required: 'question',
  steps_required: 'steps',
  scenarios_required: 'scenarios',
};

function reasonMessage(reason: string, kind: Kind): string {
  switch (reason) {
    case 'line_requires_one_cue':
      return 'Pick a cue or type a new one.';
    case 'hint_required':
      return 'Add a hint. This cue has other lines.';
    case 'hint_duplicate':
      return 'Another line on this cue already uses this hint.';
    case 'sibling_hint_missing':
      return 'Other lines on this cue need hints first. Open them from the Library and add one.';
    case 'title_required':
      return kind === 'focus' ? 'Add a title.' : 'Add a name.';
    case 'question_required':
      return 'Add the check-in question.';
    case 'steps_required':
      return 'Add at least one step.';
    case 'scenarios_required':
      return 'Add at least one scenario.';
    case 'body_required':
      return kind === 'concept' ? 'Add a definition.' : 'Add the line.';
    default:
      return 'Something in the form needs fixing.';
  }
}

/** The AI helpers' failure message; Quick add also points at the full form. */
export function aiErrorMessage(error: unknown, offerFullForm = false): string {
  if (error instanceof ApiError && (error.status === 503 || error.reason === 'ai_unavailable')) {
    return offerFullForm
      ? "The AI couldn't draft this. Try again, or use the full form."
      : "The AI couldn't draft this. Try again.";
  }
  return errorMessage(error);
}

function FieldError({ id, message }: { id: string; message?: string }) {
  if (!message) return null;
  return (
    <span className="ferr" id={id}>
      {message}
    </span>
  );
}

export function Field({
  id,
  label,
  required,
  optional,
  suggested,
  action,
  help,
  error,
  children,
}: {
  id: string;
  label: string;
  required?: boolean;
  optional?: boolean;
  /** Marks a value the AI filled in that hasn't been edited yet. */
  suggested?: boolean;
  /** A small control on the right of the label, e.g. an AI "Suggest" button. */
  action?: ReactNode;
  help?: ReactNode;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div className="field">
      <div className="labelrow">
        <label className="label" htmlFor={id}>
          {label}
          {required && <span className="req">*</span>}
          {optional && <span className="opt">optional</span>}
          {suggested && <SuggestedMark />}
        </label>
        {action}
      </div>
      {children}
      {help && !error && (
        <span className="help" id={`${id}-help`}>
          {help}
        </span>
      )}
      <FieldError id={`${id}-error`} message={error} />
    </div>
  );
}

function SuggestedMark() {
  return (
    <span className="sug">
      <SparkleIcon size={10} />
      suggested
    </span>
  );
}

function aria(id: string, error?: string, hasHelp = false) {
  return {
    id,
    'aria-invalid': error ? true : undefined,
    'aria-describedby': error ? `${id}-error` : hasHelp ? `${id}-help` : undefined,
  } as const;
}

/** Editable list of strings (scenarios, steps). */
function ListEditor({
  idPrefix,
  values,
  variant,
  multiline,
  reorder,
  addLabel,
  itemLabel,
  onChange,
}: {
  idPrefix: string;
  values: string[];
  variant: 'concept' | 'routine';
  multiline: boolean;
  reorder: boolean;
  addLabel: string;
  itemLabel: string;
  onChange: (values: string[]) => void;
}) {
  const set = (i: number, value: string) => onChange(values.map((v, j) => (j === i ? value : v)));
  const remove = (i: number) => onChange(values.length === 1 ? [''] : values.filter((_, j) => j !== i));
  const move = (i: number, by: number) => {
    const next = [...values];
    const [moved] = next.splice(i, 1);
    next.splice(i + by, 0, moved);
    onChange(next);
  };

  return (
    <>
      {values.map((value, i) => {
        const id = `${idPrefix}-${i}`;
        return (
          <div className="listitem" key={i}>
            <span className={`idx ${variant}`} aria-hidden="true">
              {i + 1}
            </span>
            <label className="sr-only" htmlFor={id}>
              {itemLabel} {i + 1}
            </label>
            {multiline ? (
              <textarea id={id} className="input" rows={2} value={value} onChange={(e) => set(i, e.target.value)} />
            ) : (
              <input id={id} className="input" value={value} onChange={(e) => set(i, e.target.value)} />
            )}
            <div className="tools">
              {reorder && (
                <>
                  <button type="button" className="iconbtn" aria-label={`Move ${itemLabel.toLowerCase()} ${i + 1} up`} disabled={i === 0} onClick={() => move(i, -1)}>
                    <UpIcon />
                  </button>
                  <button
                    type="button"
                    className="iconbtn"
                    aria-label={`Move ${itemLabel.toLowerCase()} ${i + 1} down`}
                    disabled={i === values.length - 1}
                    onClick={() => move(i, 1)}
                  >
                    <DownIcon />
                  </button>
                </>
              )}
              <button type="button" className="iconbtn" aria-label={`Remove ${itemLabel.toLowerCase()} ${i + 1}`} onClick={() => remove(i)}>
                <CloseIcon size={14} />
              </button>
            </div>
          </div>
        );
      })}
      <button type="button" className="addlink" onClick={() => onChange([...values, ''])}>
        <PlusIcon />
        {addLabel}
      </button>
    </>
  );
}

export function KindSwitch({ kind, locked, onChange }: { kind: Kind; locked?: boolean; onChange: (kind: Kind) => void }) {
  return (
    <div className="seg" role="group" aria-label="Kind">
      {KINDS.map((k) => (
        <button
          key={k.key}
          type="button"
          aria-pressed={kind === k.key}
          disabled={locked && kind !== k.key}
          onClick={() => !locked && onChange(k.key)}
        >
          {k.label}
        </button>
      ))}
    </div>
  );
}

// ---------- state, validation and save ----------

export function useItemForm({ itemId, initial, cues, lines }: { itemId: string | null; initial: Form; cues: Cue[]; lines: Item[] }) {
  const [form, setForm] = useState<Form>(initial);
  const [errors, setErrors] = useState<Errors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [suggested, setSuggested] = useState<ReadonlySet<SuggestKey>>(() => new Set());

  const update = useCallback((patch: Partial<Form>) => {
    setForm((f) => ({ ...f, ...patch }));
    setErrors((e) => {
      const next = { ...e };
      for (const key of Object.keys(patch)) {
        if (key === 'cueText' || key === 'cueId' || key === 'cueType') delete next.cue;
        else delete next[key as FieldKey];
      }
      return next;
    });
    setSuggested((s) => {
      const touched = Object.keys(patch).map((k) => (k === 'cueId' || k === 'cueType' ? 'cueText' : k));
      if (!touched.some((k) => s.has(k as SuggestKey))) return s;
      const next = new Set(s);
      for (const k of touched) next.delete(k as SuggestKey);
      return next;
    });
  }, []);

  /** Fill fields from the AI and mark them as suggested. */
  const fill = useCallback(
    (patch: Partial<Form>) => {
      update(patch);
      setSuggested((s) => new Set([...s, ...(Object.keys(patch) as SuggestKey[])]));
    },
    [update],
  );

  /** Replace the whole form, e.g. with a loaded item or a fresh AI draft. */
  const reset = useCallback((next: Form, suggestedFields: SuggestKey[] = []) => {
    setForm(next);
    setErrors({});
    setFormError(null);
    setSuggested(new Set(suggestedFields));
  }, []);

  // The existing cue the line points at: the picked one, or an exact text match.
  const resolvedCue = useMemo<Cue | null>(() => {
    if (form.cueId) return cues.find((c) => c.id === form.cueId) ?? null;
    const q = norm(form.cueText);
    return q ? cues.find((c) => norm(c.text) === q) ?? null : null;
  }, [cues, form.cueId, form.cueText]);

  const effectiveCueType: CueType = resolvedCue?.type ?? form.cueType;
  const siblings = useMemo(
    () => (resolvedCue ? lines.filter((l) => l.cue?.id === resolvedCue.id && l.id !== itemId) : []),
    [lines, resolvedCue, itemId],
  );
  const hintRequired = siblings.length >= 1;
  const loneSibling = siblings.length === 1 && !siblings[0].hint ? siblings[0] : null;

  const setCueType = (type: CueType) => {
    if (resolvedCue && resolvedCue.type !== type) update({ cueType: type, cueId: null, cueText: '', siblingHint: '' });
    else update({ cueType: type });
  };

  const validate = (): Errors => {
    const e: Errors = {};
    if (form.kind === 'line') {
      if (!form.cueText.trim()) e.cue = 'Pick a cue or type a new one.';
      if (!form.lineText.trim()) e.lineText = 'Add the line.';
      const hint = norm(form.hint);
      if (hintRequired && !hint) e.hint = 'Add a hint. This cue has other lines.';
      else if (hint && siblings.some((s) => norm(s.hint) === hint)) e.hint = 'Another line on this cue already uses this hint.';
      if (loneSibling) {
        const sib = norm(form.siblingHint);
        if (!sib) e.siblingHint = 'Give the existing line a hint too.';
        else if (sib === hint) e.siblingHint = 'Use a different hint from this line.';
      }
    } else if (form.kind === 'concept') {
      if (!form.title.trim()) e.title = 'Add a name.';
      if (!form.definition.trim()) e.definition = 'Add a definition.';
      if (!form.scenarios.some((s) => s.trim())) e.scenarios = 'Add at least one scenario.';
    } else if (form.kind === 'routine') {
      if (!form.title.trim()) e.title = 'Add a name.';
      if (!form.steps.some((s) => s.trim())) e.steps = 'Add at least one step.';
    } else {
      if (!form.title.trim()) e.title = 'Add a title.';
      if (!form.question.trim()) e.question = 'Add the check-in question.';
    }
    return e;
  };

  const persist = async () => {
    const scenarios = form.scenarios.map((s) => s.trim()).filter(Boolean);
    const steps = form.steps.map((s) => s.trim()).filter(Boolean);

    switch (form.kind) {
      case 'line': {
        if (loneSibling && form.siblingHint.trim()) {
          await updateItem(loneSibling.id, { hint: form.siblingHint.trim() });
        }
        const fields = {
          hint: orNull(form.hint),
          body: form.lineText.trim(),
          delivery_note: orNull(form.deliveryNote),
          source: orNull(form.source),
          audience: form.audience,
        };
        if (itemId) {
          const cueId = resolvedCue?.id ?? (await createCue(form.cueText.trim(), form.cueType)).id;
          await updateItem(itemId, { cue_id: cueId, ...fields });
        } else {
          await createItem({
            kind: 'line',
            cue_id: resolvedCue?.id ?? null,
            new_cue: resolvedCue ? null : { text: form.cueText.trim(), type: form.cueType },
            ...fields,
          });
        }
        return;
      }
      case 'concept': {
        const fields = { title: form.title.trim(), body: form.definition.trim(), scenarios, audience: form.audience };
        if (itemId) await updateItem(itemId, fields);
        else await createItem({ kind: 'concept', ...fields });
        return;
      }
      case 'routine': {
        const fields = { title: form.title.trim(), steps, source: orNull(form.source), audience: form.audience };
        if (itemId) await updateItem(itemId, fields);
        else await createItem({ kind: 'routine', ...fields });
        return;
      }
      case 'focus': {
        const fields = { title: form.title.trim(), question: form.question.trim(), body: orNull(form.why), audience: form.audience };
        if (itemId) await updateItem(itemId, fields);
        else await createItem({ kind: 'focus', ...fields });
        return;
      }
    }
  };

  /** Validate, save, and map backend errors onto fields. Resolves true when saved. */
  const submit = async (): Promise<boolean> => {
    setFormError(null);
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length > 0) return false;

    setSaving(true);
    try {
      await persist();
      return true;
    } catch (e) {
      if (e instanceof ApiError && e.status === 422 && e.reason) {
        const field: FieldKey | undefined =
          e.reason === 'body_required' ? (form.kind === 'concept' ? 'definition' : 'lineText') : REASON_FIELD[e.reason];
        if (field) setErrors({ [field]: reasonMessage(e.reason, form.kind) });
        else setFormError(reasonMessage(e.reason, form.kind));
      } else {
        setFormError(errorMessage(e));
      }
      return false;
    } finally {
      setSaving(false);
    }
  };

  return {
    form,
    update,
    fill,
    reset,
    errors,
    setErrors,
    formError,
    saving,
    suggested,
    resolvedCue,
    effectiveCueType,
    siblings,
    hintRequired,
    loneSibling,
    setCueType,
    submit,
  };
}

export type ItemFormState = ReturnType<typeof useItemForm>;

// ---------- fields ----------

const AUDIENCE_HELP: Record<Audience, string> = {
  everyone: "Shows in every signed-in user's Recall tab.",
  admin: 'Only shows in your own Recall tab.',
};

/** Who practises the item. Picking one stops kind switches from resetting it. */
function AudienceField({ value, onChange }: { value: Audience; onChange: (audience: Audience) => void }) {
  return (
    <div className="field">
      <span className="label" id="audience-label">
        Who sees it
      </span>
      <div className="seg two" role="group" aria-labelledby="audience-label" aria-describedby="audience-help">
        <button type="button" aria-pressed={value === 'everyone'} onClick={() => onChange('everyone')}>
          Everyone
        </button>
        <button type="button" aria-pressed={value === 'admin'} onClick={() => onChange('admin')}>
          <span className="segico">
            <LockIcon size={11} />
          </span>
          Only me
        </button>
      </div>
      <span className="help" id="audience-help">
        {AUDIENCE_HELP[value]}
      </span>
    </div>
  );
}

/** The "Only me" marker used in the Library and on previews. */
export function OnlyMeChip() {
  return (
    <span className="chip k-muted">
      <LockIcon size={10} />
      Only me
    </span>
  );
}

function SiblingsPanel({ siblings }: { siblings: Item[] }) {
  return (
    <>
      <span className="eyebrow">Already on this cue &middot; {siblings.length}</span>
      {siblings.map((s) => (
        <div className="srow" key={s.id}>
          {s.hint ? <span className="tag">{s.hint}</span> : <span className="tag none">no hint</span>}
          <span className="t">{s.body}</span>
        </div>
      ))}
    </>
  );
}

function Preview({ audience, children }: { audience: Audience; children: ReactNode }) {
  return (
    <div className="preview">
      <div className="labelrow">
        <span className="eyebrow">Preview in practice</span>
        {audience === 'admin' && <OnlyMeChip />}
      </div>
      <div className="card">{children}</div>
    </div>
  );
}

/**
 * The kind-specific fields, laid out as a main column and a side column (the
 * practice preview, and for lines the cue's other lines). On a phone the side
 * column follows the fields; on desktop it sits sticky on the right. `lead`
 * and `tail` go at the top and bottom of the main column (kind switch, errors,
 * Pause/Archive).
 *
 * `variant="draft"` is Quick add's compact card: it shows whether the cue
 * matches an existing one, leaves out Source, and shows the preview on desktop
 * only.
 */
export function ItemFields({
  state,
  cues,
  variant,
  lead,
  tail,
}: {
  state: ItemFormState;
  cues: Cue[];
  variant: 'form' | 'draft';
  lead?: ReactNode;
  tail?: ReactNode;
}) {
  const { form, update, fill, errors, setErrors, suggested, resolvedCue, effectiveCueType, siblings, hintRequired, loneSibling, setCueType } = state;
  const isDraft = variant === 'draft';
  const [busy, setBusy] = useState<'hint' | 'siblingHint' | 'scenarios' | null>(null);
  // The draft card keeps the phone compact: its preview only shows on desktop.
  const previewClass = isDraft ? 'only-desktop' : '';

  const askHint = async (target: 'hint' | 'siblingHint', body: string) => {
    setBusy(target);
    try {
      const { hint } = await suggestHint({
        cue_id: resolvedCue?.id ?? null,
        cue_text: resolvedCue ? null : orNull(form.cueText),
        body: body.trim(),
      });
      fill({ [target]: hint } as Partial<Form>);
    } catch (e) {
      setErrors((prev) => ({ ...prev, [target]: aiErrorMessage(e) }) as Errors);
    } finally {
      setBusy(null);
    }
  };

  const askScenarios = async () => {
    setBusy('scenarios');
    try {
      const existing = form.scenarios.map((s) => s.trim()).filter(Boolean);
      const { scenarios } = await draftScenarios({ title: form.title.trim(), body: orNull(form.definition), existing, count: 3 });
      fill({ scenarios: [...existing, ...scenarios] });
    } catch (e) {
      setErrors((prev) => ({ ...prev, scenarios: aiErrorMessage(e) }));
    } finally {
      setBusy(null);
    }
  };

  const suggestButton = (target: 'hint' | 'siblingHint', body: string) => (
    <button type="button" className="textbtn ai" disabled={busy !== null || !body.trim()} onClick={() => void askHint(target, body)}>
      <SparkleIcon size={11} />
      {busy === target ? 'Suggesting…' : 'Suggest'}
    </button>
  );

  const sourceField = (
    <Field id="source" label="Source" optional>
      <input id="source" className="input" value={form.source} onChange={(e) => update({ source: e.target.value })} />
    </Field>
  );

  const audienceField = (
    <AudienceField value={form.audience} onChange={(audience) => update({ audience, audienceTouched: true })} />
  );

  let main: ReactNode = null;
  let side: ReactNode = null;

  if (form.kind === 'line') {
    main = (
      <>
        <div className="field">
          <div className="labelrow">
            <label className="label" htmlFor="cue">
              Cue <span className="req">*</span>
              {suggested.has('cueText') && <SuggestedMark />}
            </label>
          </div>
          <div className="seg two" role="group" aria-label="Cue type">
            <button type="button" aria-pressed={effectiveCueType === 'reaction'} onClick={() => setCueType('reaction')}>
              She says
            </button>
            <button type="button" aria-pressed={effectiveCueType === 'goal'} onClick={() => setCueType('goal')}>
              Goal
            </button>
          </div>
          <CueCombobox
            cues={cues}
            type={effectiveCueType}
            text={form.cueText}
            resolved={resolvedCue}
            error={errors.cue}
            onText={(cueText) => update({ cueText, cueId: null, siblingHint: '' })}
            onPick={(cue) => update({ cueId: cue.id, cueText: cue.text, cueType: cue.type, siblingHint: '' })}
          />
          {isDraft && !errors.cue && form.cueText.trim() && (
            resolvedCue ? (
              <span className="match" id="cue-help">
                <CheckIcon size={11} />
                Matches an existing cue &middot; {resolvedCue.line_count} {resolvedCue.line_count === 1 ? 'line' : 'lines'}
              </span>
            ) : (
              <span className="chip k-muted" id="cue-help">
                New cue
              </span>
            )
          )}
          {!isDraft && !errors.cue && form.cueText.trim() && !resolvedCue && (
            <span className="help" id="cue-help">
              This creates a new cue.
            </span>
          )}
          <FieldError id="cue-error" message={errors.cue} />
        </div>

        {siblings.length > 0 && (
          <div className="sibs only-phone">
            <SiblingsPanel siblings={siblings} />
          </div>
        )}

        {loneSibling && (
          <Field
            id="sibling-hint"
            label="Hint for the existing line"
            required
            suggested={suggested.has('siblingHint')}
            action={suggestButton('siblingHint', loneSibling.body ?? '')}
            help={`Once a cue has two lines, both need a hint. Existing line: “${loneSibling.body ?? ''}”`}
            error={errors.siblingHint}
          >
            <input
              {...aria('sibling-hint', errors.siblingHint, true)}
              className="input"
              placeholder="e.g. agree & amplify"
              value={form.siblingHint}
              onChange={(e) => update({ siblingHint: e.target.value })}
            />
          </Field>
        )}

        <Field
          id="hint"
          label="Hint"
          required={hintRequired}
          optional={!hintRequired}
          suggested={suggested.has('hint')}
          action={hintRequired ? suggestButton('hint', form.lineText) : undefined}
          help={
            hintRequired
              ? 'Needed because this cue has other lines. Keep it different from the hints above.'
              : 'Only needed once a cue has more than one line.'
          }
          error={errors.hint}
        >
          <input
            {...aria('hint', errors.hint, true)}
            className="input"
            placeholder="e.g. own it"
            value={form.hint}
            onChange={(e) => update({ hint: e.target.value })}
          />
        </Field>

        <Field id="line-text" label="Line" required suggested={suggested.has('lineText')} error={errors.lineText}>
          <textarea
            {...aria('line-text', errors.lineText)}
            className="input"
            rows={3}
            value={form.lineText}
            onChange={(e) => update({ lineText: e.target.value })}
          />
        </Field>

        <Field id="delivery-note" label="How to say it" optional suggested={suggested.has('deliveryNote')}>
          <textarea
            id="delivery-note"
            className="input"
            rows={2}
            placeholder="e.g. Deadpan. Hold eye contact and only smile after."
            value={form.deliveryNote}
            onChange={(e) => update({ deliveryNote: e.target.value })}
          />
        </Field>

        {!isDraft && sourceField}
        {audienceField}
      </>
    );
    side = (
      <>
        {siblings.length > 0 && (
          <div className="sibs only-desktop">
            <SiblingsPanel siblings={siblings} />
          </div>
        )}
        <div className={previewClass}>
          <Preview audience={form.audience}>
            <span className="eyebrow">{effectiveCueType === 'reaction' ? 'She says' : 'Goal'}</span>
            <h3 className="cue">
              {form.cueText.trim() ? (
                effectiveCueType === 'reaction' ? (
                  quote(form.cueText.trim())
                ) : (
                  form.cueText.trim()
                )
              ) : (
                <span className="placeholder">Your cue</span>
              )}
            </h3>
            {form.hint.trim() && (
              <div className="hintrow">
                <span>Answer with</span>
                <span className="hint">{form.hint.trim()}</span>
              </div>
            )}
          </Preview>
        </div>
      </>
    );
  } else if (form.kind === 'concept') {
    const firstScenario = form.scenarios.find((s) => s.trim());
    main = (
      <>
        <Field id="title" label="Name" required suggested={suggested.has('title')} error={errors.title}>
          <input {...aria('title', errors.title)} className="input" placeholder="e.g. Push-pull" value={form.title} onChange={(e) => update({ title: e.target.value })} />
        </Field>
        <Field id="definition" label="Definition" required suggested={suggested.has('definition')} error={errors.definition}>
          <textarea
            {...aria('definition', errors.definition)}
            className="input"
            rows={3}
            value={form.definition}
            onChange={(e) => update({ definition: e.target.value })}
          />
        </Field>
        <div className="field">
          <span className="label">
            Scenarios &middot; {form.scenarios.filter((s) => s.trim()).length} <span className="req">*</span>
            {suggested.has('scenarios') && <SuggestedMark />}
          </span>
          <span className="help">Practice shows one at a time and moves to the next each time the card comes up.</span>
        </div>
        <ListEditor
          idPrefix="scenario"
          values={form.scenarios}
          variant="concept"
          multiline
          reorder={false}
          addLabel="Add scenario"
          itemLabel="Scenario"
          onChange={(scenarios) => update({ scenarios })}
        />
        <div className="btnrow">
          <button
            type="button"
            className="btn ghost sm"
            disabled={busy !== null || !form.title.trim()}
            title={form.title.trim() ? undefined : 'Add a name first'}
            onClick={() => void askScenarios()}
          >
            <span className="ai-ico">
              <SparkleIcon size={13} />
            </span>
            {busy === 'scenarios' ? 'Drafting…' : 'Draft 3 more'}
          </button>
        </div>
        <FieldError id="scenarios-error" message={errors.scenarios} />
        {audienceField}
      </>
    );
    // Concepts and routines had no preview on the phone; it's a desktop extra.
    side = (
      <div className="only-desktop">
        <Preview audience={form.audience}>
          <span className="chip k-concept">Concept</span>
          <span className="eyebrow">Which concept is this?</span>
          <p className="scenario">{firstScenario?.trim() || <span className="placeholder">A scenario</span>}</p>
          <div className="reveal">
            <p className="answer">{form.title.trim() || <span className="placeholder">Concept name</span>}</p>
            {form.definition.trim() && <p className="sub">{form.definition.trim()}</p>}
          </div>
        </Preview>
      </div>
    );
  } else if (form.kind === 'routine') {
    const steps = form.steps.map((s) => s.trim()).filter(Boolean);
    main = (
      <>
        <Field id="title" label="Name" required suggested={suggested.has('title')} error={errors.title}>
          <input {...aria('title', errors.title)} className="input" placeholder="e.g. Day-game stop" value={form.title} onChange={(e) => update({ title: e.target.value })} />
        </Field>
        <div className="field">
          <span className="label">
            Steps &middot; {form.steps.filter((s) => s.trim()).length} <span className="req">*</span>
            {suggested.has('steps') && <SuggestedMark />}
          </span>
        </div>
        <ListEditor
          idPrefix="step"
          values={form.steps}
          variant="routine"
          multiline={false}
          reorder
          addLabel="Add step"
          itemLabel="Step"
          onChange={(next) => update({ steps: next })}
        />
        <FieldError id="steps-error" message={errors.steps} />
        {!isDraft && sourceField}
        {audienceField}
      </>
    );
    side = (
      <div className="only-desktop">
        <Preview audience={form.audience}>
          <span className="chip k-routine">Routine</span>
          <span className="eyebrow">Recall the steps</span>
          <h3 className="cue">{form.title.trim() || <span className="placeholder">Routine name</span>}</h3>
          {steps.length > 0 && (
            <div className="reveal">
              <ol className="steps">
                {steps.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </div>
          )}
        </Preview>
      </div>
    );
  } else {
    main = (
      <>
        <Field id="title" label="Title" required suggested={suggested.has('title')} error={errors.title}>
          <input {...aria('title', errors.title)} className="input" placeholder="e.g. Fix sleep" value={form.title} onChange={(e) => update({ title: e.target.value })} />
        </Field>
        <Field
          id="question"
          label="Check-in question"
          required
          suggested={suggested.has('question')}
          help="Ask it as a yes/no question."
          error={errors.question}
        >
          <textarea
            {...aria('question', errors.question, true)}
            className="input"
            rows={2}
            value={form.question}
            onChange={(e) => update({ question: e.target.value })}
          />
        </Field>
        <Field id="why" label="Why it matters" optional suggested={suggested.has('why')}>
          <textarea id="why" className="input" rows={2} value={form.why} onChange={(e) => update({ why: e.target.value })} />
        </Field>
        {audienceField}
      </>
    );
    side = (
      <div className={`sidestack ${previewClass}`}>
        <Preview audience={form.audience}>
          <span className="chip k-focus">Focus check-in</span>
          <h3 className="cue">{form.title.trim() || <span className="placeholder">Your focus</span>}</h3>
          <p className="sub">{form.question.trim() || 'Your yes/no question'}</p>
        </Preview>
        <span className="help">Shows at the start of every session while it's active. Pause it when you're done with it.</span>
      </div>
    );
  }

  return (
    <div className="formgrid">
      <div className="formmain">
        {lead}
        {main}
      </div>
      <div className="formside">{side}</div>
      {tail && <div className="formtail">{tail}</div>}
    </div>
  );
}
