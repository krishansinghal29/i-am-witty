/**
 * Manage cues: rename a cue, switch She says / Goal, or merge a duplicate into
 * another cue (its lines move over and the duplicate is removed). One row is
 * edited at a time; merging asks for an inline confirm, never a browser dialog.
 */

import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listCues, mergeCue, updateCue } from '@/api/recall';
import { ApiError, errorMessage } from '@/api/http';
import type { Cue, CueType } from '@/api/types';
import { BackIcon } from '@/components/Icons';
import { useToast } from '@/components/Toast';

type Mode =
  | { kind: 'edit'; cueId: string; text: string; type: CueType }
  | { kind: 'merge'; cueId: string; intoId: string; confirming: boolean };

function quote(text: string) {
  return `“${text}”`;
}

function lines(n: number) {
  return `${n} ${n === 1 ? 'line' : 'lines'}`;
}

function shown(cue: Cue) {
  return cue.type === 'reaction' ? quote(cue.text) : cue.text;
}

function renameError(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.status === 409) return 'Another cue already has this text. Merge them instead.';
    if (e.reason === 'text_required') return 'Add the cue text.';
    if (e.status === 404) return "That cue doesn't exist anymore. Refresh and try again.";
  }
  return errorMessage(e);
}

function mergeError(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.reason === 'sibling_hint_missing' || e.reason === 'hint_duplicate') {
      return 'Every line needs a different hint before these cues can be merged. Add hints first.';
    }
    if (e.reason === 'merge_same_cue') return 'Pick a different cue to merge into.';
    if (e.status === 404) return "One of these cues doesn't exist anymore. Refresh and try again.";
  }
  return errorMessage(e);
}

export function CuesPage() {
  const toast = useToast();
  const [cues, setCues] = useState<Cue[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode | null>(null);
  const [rowError, setRowError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setCues(await listCues());
      setLoadError(null);
    } catch (e) {
      setLoadError(errorMessage(e));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const open = (next: Mode | null) => {
    setMode(next);
    setRowError(null);
  };

  const saveEdit = async () => {
    if (mode?.kind !== 'edit') return;
    if (!mode.text.trim()) {
      setRowError('Add the cue text.');
      return;
    }
    setBusy(true);
    try {
      await updateCue(mode.cueId, { text: mode.text.trim(), type: mode.type });
      toast('Saved');
      open(null);
      await load();
    } catch (e) {
      setRowError(renameError(e));
    } finally {
      setBusy(false);
    }
  };

  const doMerge = async () => {
    if (mode?.kind !== 'merge' || !cues) return;
    const target = cues.find((c) => c.id === mode.intoId);
    setBusy(true);
    try {
      await mergeCue(mode.cueId, mode.intoId);
      toast(target ? `Merged into ${shown(target)}` : 'Merged');
      open(null);
      await load();
    } catch (e) {
      setRowError(mergeError(e));
      setMode({ ...mode, confirming: false });
    } finally {
      setBusy(false);
    }
  };

  const groups: { type: CueType; label: string }[] = [
    { type: 'reaction', label: 'She says' },
    { type: 'goal', label: 'Goals' },
  ];

  const renderRow = (cue: Cue) => {
    const editing = mode?.kind === 'edit' && mode.cueId === cue.id ? mode : null;
    const merging = mode?.kind === 'merge' && mode.cueId === cue.id ? mode : null;
    const target = merging ? cues?.find((c) => c.id === merging.intoId) ?? null : null;
    const others = (cues ?? []).filter((c) => c.id !== cue.id);

    if (editing) {
      return (
        <div className="cuerow open" key={cue.id}>
          <label className="label" htmlFor={`cue-text-${cue.id}`}>
            Cue text
          </label>
          <input
            id={`cue-text-${cue.id}`}
            className="input"
            value={editing.text}
            aria-invalid={rowError ? true : undefined}
            aria-describedby={rowError ? `cue-row-error-${cue.id}` : undefined}
            onChange={(e) => setMode({ ...editing, text: e.target.value })}
          />
          <div className="seg two" role="group" aria-label="Cue type">
            <button type="button" aria-pressed={editing.type === 'reaction'} onClick={() => setMode({ ...editing, type: 'reaction' })}>
              She says
            </button>
            <button type="button" aria-pressed={editing.type === 'goal'} onClick={() => setMode({ ...editing, type: 'goal' })}>
              Goal
            </button>
          </div>
          {rowError && (
            <span className="ferr" id={`cue-row-error-${cue.id}`}>
              {rowError}
            </span>
          )}
          <div className="btnrow">
            <button type="button" className="btn ghost sm" disabled={busy} onClick={() => open(null)}>
              Cancel
            </button>
            <button type="button" className="btn warm sm" disabled={busy} onClick={() => void saveEdit()}>
              {busy ? 'Saving…' : 'Save'}
            </button>
          </div>
        </div>
      );
    }

    if (merging) {
      return (
        <div className="cuerow open" key={cue.id}>
          <div className="gt">
            <span className="eyebrow">{cue.type === 'reaction' ? 'She says' : 'Goal'}</span>
            <b>{shown(cue)}</b>
          </div>
          {merging.confirming && target ? (
            <>
              <p className="sub">
                Move {lines(cue.line_count)} from {shown(cue)} into {shown(target)} and remove {shown(cue)}?
              </p>
              <div className="btnrow">
                <button type="button" className="btn ghost sm" disabled={busy} onClick={() => setMode({ ...merging, confirming: false })}>
                  Cancel
                </button>
                <button type="button" className="btn danger-fill sm" disabled={busy} onClick={() => void doMerge()}>
                  {busy ? 'Merging…' : 'Merge'}
                </button>
              </div>
            </>
          ) : (
            <>
              <label className="label" htmlFor={`merge-into-${cue.id}`}>
                Merge into
              </label>
              <select
                id={`merge-into-${cue.id}`}
                className="input"
                value={merging.intoId}
                onChange={(e) => {
                  setMode({ ...merging, intoId: e.target.value });
                  setRowError(null);
                }}
              >
                <option value="">Pick a cue…</option>
                {others.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.type === 'reaction' ? 'She says' : 'Goal'}: {c.text} ({lines(c.line_count)})
                  </option>
                ))}
              </select>
              {rowError && <span className="ferr">{rowError}</span>}
              <div className="btnrow">
                <button type="button" className="btn ghost sm" onClick={() => open(null)}>
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn warm sm"
                  disabled={!merging.intoId}
                  onClick={() => {
                    setMode({ ...merging, confirming: true });
                    setRowError(null);
                  }}
                >
                  Continue
                </button>
              </div>
            </>
          )}
        </div>
      );
    }

    return (
      <div className="cuerow" key={cue.id}>
        <div className="gt">
          <b>{shown(cue)}</b>
          <span className="m">{lines(cue.line_count)}</span>
        </div>
        <div className="cueacts">
          <button type="button" className="textbtn" onClick={() => open({ kind: 'edit', cueId: cue.id, text: cue.text, type: cue.type })}>
            Edit
          </button>
          {others.length > 0 && (
            <button type="button" className="textbtn" onClick={() => open({ kind: 'merge', cueId: cue.id, intoId: '', confirming: false })}>
              Merge into…
            </button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="screen">
      <header className="appbar">
        <Link className="iconbtn only-phone" to="/admin" aria-label="Back to library">
          <BackIcon />
        </Link>
        <span className="ttl">Cues</span>
      </header>
      <main className="body">
        <p className="sub">Rename a cue, switch it between She says and Goal, or merge a duplicate into another cue. Its lines move over.</p>
        {loadError ? (
          <div className="banner error" role="alert">
            <span>{loadError}</span>
            <button type="button" className="btn ghost sm" style={{ alignSelf: 'flex-start' }} onClick={() => void load()}>
              Try again
            </button>
          </div>
        ) : cues === null ? (
          <div className="loading" aria-label="Loading">
            <div className="spinner" />
          </div>
        ) : cues.length === 0 ? (
          <div className="card empty">
            <b>No cues yet.</b>
            <p className="sub">Cues are created when you add a line.</p>
          </div>
        ) : (
          <div className="cuegrid">
            {groups.map((g) => {
              const inGroup = cues.filter((c) => c.type === g.type);
              if (inGroup.length === 0) return null;
              return (
                <section className="group" key={g.type} aria-label={g.label}>
                  <div className="group-h">
                    <div className="gt">
                      <span className="eyebrow">{g.label}</span>
                      <b>{inGroup.length === 1 ? '1 cue' : `${inGroup.length} cues`}</b>
                    </div>
                  </div>
                  {inGroup.map(renderRow)}
                </section>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
