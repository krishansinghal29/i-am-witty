/**
 * New item and Edit item share this form. The kind picks which fields show;
 * on edit the kind is locked and Pause/Resume and Archive appear.
 */

import { useEffect, useMemo, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { createCue, createItem, getItem, listCues, listItems, updateItem } from '@/api/recall';
import { ApiError, errorMessage } from '@/api/http';
import type { Cue, CueType, Item, Kind, Status } from '@/api/types';
import { BackIcon, CloseIcon, DownIcon, PlusIcon, UpIcon } from '@/components/Icons';
import { useToast } from '@/components/Toast';
import { CueCombobox } from './CueCombobox';

const KINDS: { key: Kind; label: string; noun: string }[] = [
  { key: 'line', label: 'Line', noun: 'line' },
  { key: 'concept', label: 'Concept', noun: 'concept' },
  { key: 'routine', label: 'Routine', noun: 'routine' },
  { key: 'focus', label: 'Focus', noun: 'focus' },
];

function parseKind(value: string | null): Kind {
  return KINDS.some((k) => k.key === value) ? (value as Kind) : 'line';
}

function noun(kind: Kind) {
  return KINDS.find((k) => k.key === kind)?.noun ?? 'item';
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

interface Form {
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
}

function emptyForm(kind: Kind): Form {
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
  };
}

function formFromItem(item: Item): Form {
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
  };
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

function FieldError({ id, message }: { id: string; message?: string }) {
  if (!message) return null;
  return (
    <span className="ferr" id={id}>
      {message}
    </span>
  );
}

function Field({
  id,
  label,
  required,
  optional,
  help,
  error,
  children,
}: {
  id: string;
  label: string;
  required?: boolean;
  optional?: boolean;
  help?: ReactNode;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div className="field">
      <label className="label" htmlFor={id}>
        {label}
        {required && <span className="req">*</span>}
        {optional && <span className="opt">optional</span>}
      </label>
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

const STATUS_LABEL: Record<Status, string> = { active: 'Active', paused: 'Paused', archived: 'Archived' };

export function ItemFormRoute() {
  const { id } = useParams();
  const [params] = useSearchParams();
  return <ItemForm key={id ?? 'new'} itemId={id ?? null} initialKind={parseKind(params.get('kind'))} />;
}

function ItemForm({ itemId, initialKind }: { itemId: string | null; initialKind: Kind }) {
  const navigate = useNavigate();
  const toast = useToast();
  const [, setParams] = useSearchParams();
  const isEdit = itemId !== null;

  const [form, setForm] = useState<Form>(() => emptyForm(initialKind));
  const [status, setStatus] = useState<Status>('active');
  const [cues, setCues] = useState<Cue[]>([]);
  const [lines, setLines] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Errors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [statusBusy, setStatusBusy] = useState(false);
  const [confirmArchive, setConfirmArchive] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [cueList, lineList, item] = await Promise.all([
          listCues(),
          listItems({ kind: 'line' }),
          itemId ? getItem(itemId) : Promise.resolve(null),
        ]);
        if (cancelled) return;
        setCues(cueList);
        setLines(lineList);
        if (item) {
          setForm(formFromItem(item));
          setStatus(item.status);
        }
      } catch (e) {
        if (!cancelled) setLoadError(errorMessage(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [itemId]);

  const update = (patch: Partial<Form>) => {
    setForm((f) => ({ ...f, ...patch }));
    setErrors((e) => {
      const next = { ...e };
      for (const key of Object.keys(patch)) {
        if (key === 'cueText' || key === 'cueId' || key === 'cueType') delete next.cue;
        else delete next[key as FieldKey];
      }
      return next;
    });
  };

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

  const setKind = (kind: Kind) => {
    update({ kind });
    setParams({ kind }, { replace: true });
  };

  const setCueType = (type: CueType) => {
    if (resolvedCue && resolvedCue.type !== type) update({ cueType: type, cueId: null, cueText: '' });
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
        const fields = { title: form.title.trim(), body: form.definition.trim(), scenarios };
        if (itemId) await updateItem(itemId, fields);
        else await createItem({ kind: 'concept', ...fields });
        return;
      }
      case 'routine': {
        const fields = { title: form.title.trim(), steps, source: orNull(form.source) };
        if (itemId) await updateItem(itemId, fields);
        else await createItem({ kind: 'routine', ...fields });
        return;
      }
      case 'focus': {
        const fields = { title: form.title.trim(), question: form.question.trim(), body: orNull(form.why) };
        if (itemId) await updateItem(itemId, fields);
        else await createItem({ kind: 'focus', ...fields });
        return;
      }
    }
  };

  const save = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length > 0) return;

    setSaving(true);
    try {
      await persist();
      toast('Saved');
      navigate('/admin');
    } catch (e) {
      if (e instanceof ApiError && e.status === 422 && e.reason) {
        const field: FieldKey | undefined =
          e.reason === 'body_required' ? (form.kind === 'concept' ? 'definition' : 'lineText') : REASON_FIELD[e.reason];
        if (field) setErrors({ [field]: reasonMessage(e.reason, form.kind) });
        else setFormError(reasonMessage(e.reason, form.kind));
      } else {
        setFormError(errorMessage(e));
      }
    } finally {
      setSaving(false);
    }
  };

  const changeStatus = async (next: Status) => {
    if (!itemId) return;
    setStatusBusy(true);
    try {
      const item = await updateItem(itemId, { status: next });
      setStatus(item.status);
      setConfirmArchive(false);
      if (next === 'archived') {
        toast('Archived');
        navigate('/admin');
      } else {
        toast(next === 'paused' ? 'Paused' : status === 'archived' ? 'Restored' : 'Resumed');
      }
    } catch (e) {
      toast(errorMessage(e), { tone: 'error' });
    } finally {
      setStatusBusy(false);
    }
  };

  const title = isEdit ? `Edit ${noun(form.kind)}` : 'New item';

  const appbar = (
    <header className="appbar">
      <Link className="iconbtn" to="/admin" aria-label="Back to library">
        <BackIcon />
      </Link>
      <span className="ttl">{title}</span>
      {isEdit && !loading && (
        <span className={`chip ${status === 'active' ? `k-${form.kind}` : 'k-muted'}`}>{STATUS_LABEL[status]}</span>
      )}
    </header>
  );

  if (loading || loadError) {
    return (
      <div className="screen">
        {appbar}
        <main className="body">
          {loadError ? (
            <div className="banner error" role="alert">
              <span>{loadError}</span>
            </div>
          ) : (
            <div className="loading" aria-label="Loading">
              <div className="spinner" />
            </div>
          )}
        </main>
      </div>
    );
  }

  return (
    <form className="screen" onSubmit={(e) => void save(e)} noValidate>
      {appbar}
      <main className="body">
        <div className="seg" role="group" aria-label="Kind">
          {KINDS.map((k) => (
            <button
              key={k.key}
              type="button"
              aria-pressed={form.kind === k.key}
              disabled={isEdit && form.kind !== k.key}
              onClick={() => !isEdit && setKind(k.key)}
            >
              {k.label}
            </button>
          ))}
        </div>

        {formError && (
          <div className="banner error" role="alert">
            <span>{formError}</span>
          </div>
        )}

        {form.kind === 'line' && (
          <>
            <div className="field">
              <label className="label" htmlFor="cue">
                Cue <span className="req">*</span>
              </label>
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
                onText={(cueText) => update({ cueText, cueId: null })}
                onPick={(cue) => update({ cueId: cue.id, cueText: cue.text, cueType: cue.type })}
              />
              {!errors.cue && form.cueText.trim() && !resolvedCue && (
                <span className="help" id="cue-help">
                  This creates a new cue.
                </span>
              )}
              <FieldError id="cue-error" message={errors.cue} />
            </div>

            {siblings.length > 0 && (
              <div className="sibs">
                <span className="eyebrow">Already on this cue &middot; {siblings.length}</span>
                {siblings.map((s) => (
                  <div className="srow" key={s.id}>
                    {s.hint ? <span className="tag">{s.hint}</span> : <span className="tag none">no hint</span>}
                    <span className="t">{s.body}</span>
                  </div>
                ))}
              </div>
            )}

            {loneSibling && (
              <Field
                id="sibling-hint"
                label="Hint for the existing line"
                required
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

            <Field id="line-text" label="Line" required error={errors.lineText}>
              <textarea
                {...aria('line-text', errors.lineText)}
                className="input"
                rows={3}
                value={form.lineText}
                onChange={(e) => update({ lineText: e.target.value })}
              />
            </Field>

            <Field id="delivery-note" label="How to say it" optional>
              <textarea
                id="delivery-note"
                className="input"
                rows={2}
                placeholder="e.g. Deadpan. Hold eye contact and only smile after."
                value={form.deliveryNote}
                onChange={(e) => update({ deliveryNote: e.target.value })}
              />
            </Field>

            <Field id="source" label="Source" optional>
              <input id="source" className="input" value={form.source} onChange={(e) => update({ source: e.target.value })} />
            </Field>

            <div className="preview">
              <span className="eyebrow">Preview in practice</span>
              <div className="card">
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
              </div>
            </div>
          </>
        )}

        {form.kind === 'concept' && (
          <>
            <Field id="title" label="Name" required error={errors.title}>
              <input {...aria('title', errors.title)} className="input" placeholder="e.g. Push-pull" value={form.title} onChange={(e) => update({ title: e.target.value })} />
            </Field>
            <Field id="definition" label="Definition" required error={errors.definition}>
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
            <FieldError id="scenarios-error" message={errors.scenarios} />
          </>
        )}

        {form.kind === 'routine' && (
          <>
            <Field id="title" label="Name" required error={errors.title}>
              <input {...aria('title', errors.title)} className="input" placeholder="e.g. Day-game stop" value={form.title} onChange={(e) => update({ title: e.target.value })} />
            </Field>
            <div className="field">
              <span className="label">
                Steps &middot; {form.steps.filter((s) => s.trim()).length} <span className="req">*</span>
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
              onChange={(steps) => update({ steps })}
            />
            <FieldError id="steps-error" message={errors.steps} />
            <Field id="source" label="Source" optional>
              <input id="source" className="input" value={form.source} onChange={(e) => update({ source: e.target.value })} />
            </Field>
          </>
        )}

        {form.kind === 'focus' && (
          <>
            <Field id="title" label="Title" required error={errors.title}>
              <input {...aria('title', errors.title)} className="input" placeholder="e.g. Fix sleep" value={form.title} onChange={(e) => update({ title: e.target.value })} />
            </Field>
            <Field id="question" label="Check-in question" required help="Ask it as a yes/no question." error={errors.question}>
              <textarea
                {...aria('question', errors.question, true)}
                className="input"
                rows={2}
                value={form.question}
                onChange={(e) => update({ question: e.target.value })}
              />
            </Field>
            <Field id="why" label="Why it matters" optional>
              <textarea id="why" className="input" rows={2} value={form.why} onChange={(e) => update({ why: e.target.value })} />
            </Field>
            <div className="preview">
              <span className="eyebrow">Preview in practice</span>
              <div className="card">
                <span className="chip k-focus">Focus check-in</span>
                <h3 className="cue">{form.title.trim() || <span className="placeholder">Your focus</span>}</h3>
                <p className="sub">{form.question.trim() || 'Your yes/no question'}</p>
              </div>
            </div>
            <span className="help">Shows at the start of every session while it's active. Pause it when you're done with it.</span>
          </>
        )}

        {isEdit && (
          <div className="zone">
            {status === 'archived' ? (
              <div className="zrow">
                <div>
                  <b>Archived</b>
                  <span>Restore it to show it in practice again.</span>
                </div>
                <div className="actions">
                  <button type="button" className="btn ghost sm" disabled={statusBusy} onClick={() => void changeStatus('active')}>
                    Restore
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="zrow">
                  <div>
                    <b>{status === 'paused' ? 'Paused' : 'Pause'}</b>
                    <span>
                      {status === 'paused'
                        ? "It won't show in practice until you resume it."
                        : 'Stops it showing in practice. Progress is kept.'}
                    </span>
                  </div>
                  <div className="actions">
                    <button
                      type="button"
                      className="btn ghost sm"
                      disabled={statusBusy}
                      onClick={() => void changeStatus(status === 'paused' ? 'active' : 'paused')}
                    >
                      {status === 'paused' ? 'Resume' : 'Pause'}
                    </button>
                  </div>
                </div>
                <div className="zrow">
                  {confirmArchive ? (
                    <>
                      <div>
                        <b>Archive this item?</b>
                        <span>It stops showing everywhere. Nothing is deleted.</span>
                      </div>
                      <div className="actions">
                        <button type="button" className="btn ghost sm" disabled={statusBusy} onClick={() => setConfirmArchive(false)}>
                          Cancel
                        </button>
                        <button type="button" className="btn danger-fill sm" disabled={statusBusy} onClick={() => void changeStatus('archived')}>
                          Archive
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <div>
                        <b>Archive</b>
                        <span>Hides it everywhere. Nothing is deleted.</span>
                      </div>
                      <div className="actions">
                        <button type="button" className="btn ghost sm danger" disabled={statusBusy} onClick={() => setConfirmArchive(true)}>
                          Archive
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </main>
      <footer className="foot">
        <button type="submit" className="btn warm" disabled={saving}>
          {saving ? 'Saving…' : isEdit ? 'Save changes' : `Save ${noun(form.kind)}`}
        </button>
      </footer>
    </form>
  );
}
