/**
 * New item and Edit item share this form. The kind picks which fields show;
 * on edit the kind is locked and Pause/Resume and Archive appear. Quick add's
 * "Full form" opens this page with its draft in router state.
 */

import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { getItem, listCues, listItems, updateItem } from '@/api/recall';
import { errorMessage } from '@/api/http';
import type { Cue, Item, Kind, Status } from '@/api/types';
import { BackIcon } from '@/components/Icons';
import { useToast } from '@/components/Toast';
import { clearQuickDraft } from '@/lib/quickDraft';
import { ItemFields, KindSwitch, emptyForm, formFromItem, noun, parseKind, switchKind, useItemForm } from './itemForm';
import type { Form } from './itemForm';

/** Router state Quick add passes when handing its draft to the full form. */
export interface FullFormHandoff {
  form: Form;
  fromQuickAdd: true;
}

function readHandoff(state: unknown): FullFormHandoff | null {
  const s = state as Partial<FullFormHandoff> | null;
  return s?.fromQuickAdd && s.form && typeof s.form.kind === 'string' ? (s as FullFormHandoff) : null;
}

const STATUS_LABEL: Record<Status, string> = { active: 'Active', paused: 'Paused', archived: 'Archived' };

export function ItemFormRoute() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const location = useLocation();
  const handoff = id ? null : readHandoff(location.state);
  return <ItemForm key={id ?? 'new'} itemId={id ?? null} initialKind={parseKind(params.get('kind'))} handoff={handoff} />;
}

function ItemForm({ itemId, initialKind, handoff }: { itemId: string | null; initialKind: Kind; handoff: FullFormHandoff | null }) {
  const navigate = useNavigate();
  const toast = useToast();
  const [, setParams] = useSearchParams();
  const isEdit = itemId !== null;

  const [cues, setCues] = useState<Cue[]>([]);
  const [lines, setLines] = useState<Item[]>([]);
  const state = useItemForm({ itemId, initial: handoff?.form ?? emptyForm(initialKind), cues, lines });
  const { form, update, reset, formError, saving, submit } = state;
  const [status, setStatus] = useState<Status>('active');
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
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
          reset(formFromItem(item));
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
  }, [itemId, reset]);

  const setKind = (kind: Kind) => {
    update(switchKind(form, kind));
    setParams({ kind }, { replace: true, state: handoff ? { ...handoff, form: { ...form, kind } } : undefined });
  };

  const save = async (event: FormEvent) => {
    event.preventDefault();
    if (!(await submit())) return;
    toast('Saved');
    if (handoff) {
      // Came from Quick add: its text is now saved, so go back for the next one.
      clearQuickDraft();
      navigate('/admin/quick');
    } else {
      navigate('/admin');
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
      <Link
        className="iconbtn only-phone"
        to={handoff ? '/admin/quick' : '/admin'}
        aria-label={handoff ? 'Back to Quick add' : 'Back to library'}
      >
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

  const statusZone = (
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
  );

  return (
    <form className="screen" onSubmit={(e) => void save(e)} noValidate>
      {appbar}
      <main className="body">
        <ItemFields
          state={state}
          cues={cues}
          variant="form"
          lead={
            <>
              <KindSwitch kind={form.kind} locked={isEdit} onChange={setKind} />
              {formError && (
                <div className="banner error" role="alert">
                  <span>{formError}</span>
                </div>
              )}
            </>
          }
          tail={isEdit ? statusZone : undefined}
        />
      </main>
      <footer className="foot">
        <button type="submit" className="btn warm" disabled={saving}>
          {saving ? 'Saving…' : isEdit ? 'Save changes' : `Save ${noun(form.kind)}`}
        </button>
      </footer>
    </form>
  );
}
