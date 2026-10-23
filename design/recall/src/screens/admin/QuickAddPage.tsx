/**
 * Quick add: paste or dictate raw text, let the AI draft an item, fix it up,
 * save. The draft is the same form state and fields as the full form, so it
 * saves the same way; "Full form" hands the draft over with every edit.
 */

import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { listCues, listItems, suggestItem } from '@/api/recall';
import { errorMessage } from '@/api/http';
import type { Cue, Item } from '@/api/types';
import { BackIcon, MicIcon, SparkleIcon } from '@/components/Icons';
import { useToast } from '@/components/Toast';
import { useDictation } from '@/lib/dictation';
import { clearQuickDraft, loadQuickDraft, saveQuickDraft } from '@/lib/quickDraft';
import { Field, ItemFields, KindSwitch, aiErrorMessage, emptyForm, formFromDraft, suggestedKeys, switchKind, useItemForm } from './itemForm';
import type { FullFormHandoff } from './ItemFormPage';

export function QuickAddPage() {
  const navigate = useNavigate();
  const toast = useToast();

  const [text, setTextState] = useState(loadQuickDraft);
  const [cues, setCues] = useState<Cue[]>([]);
  const [lines, setLines] = useState<Item[]>([]);
  const [listsError, setListsError] = useState<string | null>(null);
  const [listsReady, setListsReady] = useState(false);
  const [hasDraft, setHasDraft] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [suggestError, setSuggestError] = useState<string | null>(null);

  const state = useItemForm({ itemId: null, initial: emptyForm('line'), cues, lines });
  const { form, update, reset, formError, saving, submit } = state;

  const setText = useCallback((next: string) => {
    setTextState(next);
    saveQuickDraft(next);
  }, []);
  const dictation = useDictation(setText);

  // Cues and lines drive cue matching and the hint rules, as in the full form.
  const loadLists = useCallback(async () => {
    try {
      const [cueList, lineList] = await Promise.all([listCues(), listItems({ kind: 'line' })]);
      setCues(cueList);
      setLines(lineList);
      setListsError(null);
    } catch (e) {
      setListsError(errorMessage(e));
    } finally {
      setListsReady(true);
    }
  }, []);

  useEffect(() => {
    void loadLists();
  }, [loadLists]);

  const suggest = async () => {
    if (dictation.listening) dictation.stop();
    setSuggesting(true);
    setSuggestError(null);
    try {
      const draft = await suggestItem(text.trim());
      const next = formFromDraft(draft);
      reset(next, suggestedKeys(next));
      setHasDraft(true);
    } catch (e) {
      setSuggestError(aiErrorMessage(e, true));
    } finally {
      setSuggesting(false);
    }
  };

  const save = async (event: FormEvent) => {
    event.preventDefault();
    if (!(await submit())) return;
    toast('Saved');
    clearQuickDraft();
    setTextState('');
    setHasDraft(false);
    reset(emptyForm('line'));
    // A new cue or a sibling's new hint changes what the next draft matches against.
    void loadLists();
  };

  const openFullForm = () => {
    const handoff: FullFormHandoff = { form, fromQuickAdd: true };
    navigate(`/admin/new?kind=${form.kind}`, { state: handoff });
  };

  return (
    <form className="screen" onSubmit={(e) => void save(e)} noValidate>
      <header className="appbar">
        <Link className="iconbtn only-phone" to="/admin" aria-label="Back to library">
          <BackIcon />
        </Link>
        <span className="ttl">Quick add</span>
      </header>
      <main className="body">
        <div className="quickbox">
          <Field
            id="quick-text"
            label="Paste or dictate"
            help="Write it however it comes. The AI turns it into a draft you can edit before saving."
          >
            <textarea
              id="quick-text"
              className="input"
              rows={4}
              aria-describedby="quick-text-help"
              placeholder="e.g. when she says she's not here to meet anyone, say good because I'm not that easy, mock-serious"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </Field>

          <div className="btnrow">
            {dictation.supported && (
              <button
                type="button"
                className={`btn ghost sm${dictation.listening ? ' live' : ''}`}
                aria-pressed={dictation.listening}
                onClick={() => (dictation.listening ? dictation.stop() : dictation.start(text))}
              >
                <MicIcon />
                {dictation.listening ? 'Stop' : 'Dictate'}
              </button>
            )}
            <button type="button" className="btn cool sm" disabled={!text.trim() || suggesting || !listsReady} onClick={() => void suggest()}>
              <SparkleIcon />
              {suggesting ? 'Drafting…' : hasDraft ? 'Suggest again' : 'Suggest'}
            </button>
          </div>
          {dictation.error && <span className="ferr">{dictation.error}</span>}
        </div>

        {listsError && (
          <div className="banner error" role="alert">
            <span>{listsError}</span>
          </div>
        )}
        {suggestError && (
          <div className="banner error" role="alert">
            <span>{suggestError}</span>
          </div>
        )}

        {hasDraft && (
          <section className="draft" aria-label="Suggested draft">
            <div className="draft-h">
              <SparkleIcon />
              Suggested draft
            </div>
            <ItemFields
              state={state}
              cues={cues}
              variant="draft"
              lead={
                <>
                  <KindSwitch kind={form.kind} onChange={(kind) => update(switchKind(form, kind))} />
                  {formError && (
                    <div className="banner error" role="alert">
                      <span>{formError}</span>
                    </div>
                  )}
                </>
              }
            />
          </section>
        )}
      </main>
      {hasDraft && (
        <footer className="foot">
          <button type="button" className="btn ghost" onClick={openFullForm}>
            Full form
          </button>
          <button type="submit" className="btn warm" disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </button>
        </footer>
      )}
    </form>
  );
}
