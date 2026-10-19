import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { listItems } from '@/api/recall';
import { errorMessage } from '@/api/http';
import type { CueRef, Item, Kind } from '@/api/types';
import { PlusIcon, SearchIcon } from '@/components/Icons';
import { signOut } from '@/lib/firebase';

type Filter = 'all' | Kind;

const FILTERS: { key: Filter; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'line', label: 'Lines' },
  { key: 'concept', label: 'Concepts' },
  { key: 'routine', label: 'Routines' },
  { key: 'focus', label: 'Focus' },
];

function quote(text: string) {
  return `“${text}”`;
}

function matches(item: Item, query: string): boolean {
  if (!query) return true;
  const haystack = [item.cue?.text, item.hint, item.body, item.title, item.question]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
  return haystack.includes(query);
}

interface LineGroup {
  cue: CueRef;
  lines: Item[];
  newest: string;
}

function groupLines(lines: Item[]): LineGroup[] {
  const byCue = new Map<string, LineGroup>();
  for (const line of lines) {
    if (!line.cue) continue;
    const group = byCue.get(line.cue.id) ?? { cue: line.cue, lines: [], newest: '' };
    group.lines.push(line);
    if (line.created_at > group.newest) group.newest = line.created_at;
    byCue.set(line.cue.id, group);
  }
  const groups = [...byCue.values()];
  for (const group of groups) group.lines.sort((a, b) => a.created_at.localeCompare(b.created_at));
  // Groups with the most recent additions first.
  return groups.sort((a, b) => b.newest.localeCompare(a.newest));
}

function StatusChip({ item }: { item: Item }) {
  if (item.status === 'paused') return <span className="chip k-muted">Paused</span>;
  if (item.status === 'archived') return <span className="chip k-muted">Archived</span>;
  return null;
}

export function LibraryPage() {
  const [archived, setArchived] = useState(false);
  const [items, setItems] = useState<Item[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<Filter>('all');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setItems(null);
    setError(null);
    listItems(archived ? { status: 'archived' } : {})
      .then((result) => {
        if (!cancelled) setItems(result);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(errorMessage(e));
      });
    return () => {
      cancelled = true;
    };
  }, [archived, attempt]);

  const counts = useMemo(() => {
    const all = items ?? [];
    return {
      all: all.length,
      line: all.filter((i) => i.kind === 'line').length,
      concept: all.filter((i) => i.kind === 'concept').length,
      routine: all.filter((i) => i.kind === 'routine').length,
      focus: all.filter((i) => i.kind === 'focus').length,
    };
  }, [items]);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (items ?? []).filter((i) => (filter === 'all' || i.kind === filter) && matches(i, q));
  }, [items, query, filter]);

  const lineGroups = groupLines(visible.filter((i) => i.kind === 'line'));
  const concepts = visible.filter((i) => i.kind === 'concept');
  const routines = visible.filter((i) => i.kind === 'routine');
  const focus = visible.filter((i) => i.kind === 'focus');
  const addKind: Kind = filter === 'all' ? 'line' : filter;

  return (
    <div className="screen">
      <header className="appbar">
        <span className="ttl">{archived ? 'Archived' : 'Library'}</span>
        <Link className="btn warm sm" to={`/admin/new?kind=${addKind}`}>
          <PlusIcon />
          Add
        </Link>
      </header>
      <main className="body">
        <div className="search">
          <SearchIcon />
          <label htmlFor="library-search" className="sr-only">
            Search
          </label>
          <input
            id="library-search"
            className="input"
            type="search"
            placeholder="Search lines, cues, concepts"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        <div className="filters" role="group" aria-label="Filter by kind">
          {FILTERS.filter((f) => f.key === 'all' || counts[f.key] > 0).map((f) => (
            <button
              key={f.key}
              type="button"
              className="fchip"
              aria-pressed={filter === f.key}
              onClick={() => setFilter(f.key)}
            >
              {f.label} {counts[f.key]}
            </button>
          ))}
        </div>

        {error ? (
          <div className="banner error" role="alert">
            <span>{error}</span>
            <button type="button" className="btn ghost sm" style={{ alignSelf: 'flex-start' }} onClick={() => setAttempt((n) => n + 1)}>
              Try again
            </button>
          </div>
        ) : items === null ? (
          <div className="loading" aria-label="Loading">
            <div className="spinner" />
          </div>
        ) : items.length === 0 ? (
          <div className="card empty">
            <b>{archived ? 'Nothing archived.' : 'Nothing here yet.'}</b>
            {!archived && (
              <>
                <p className="sub">Add your first line and it shows up in practice tomorrow.</p>
                <Link className="btn warm sm" to="/admin/new?kind=line">
                  Add a line
                </Link>
              </>
            )}
          </div>
        ) : visible.length === 0 ? (
          <div className="card empty">
            <b>No matches.</b>
            <p className="sub">Try a different search or filter.</p>
          </div>
        ) : (
          <>
            {lineGroups.map((group) => (
              <section className="group" key={group.cue.id}>
                <div className="group-h">
                  <div className="gt">
                    <span className="eyebrow">{group.cue.type === 'reaction' ? 'She says' : 'Goal'}</span>
                    <b>{group.cue.type === 'reaction' ? quote(group.cue.text) : group.cue.text}</b>
                  </div>
                  <span className="n">{group.lines.length}</span>
                </div>
                {group.lines.map((line) => (
                  <Link className="row" key={line.id} to={`/admin/items/${line.id}`}>
                    {line.hint && <span className="tag">{line.hint}</span>}
                    <span className="t">{line.body}</span>
                    <StatusChip item={line} />
                  </Link>
                ))}
              </section>
            ))}

            {concepts.length > 0 && (
              <section className="group">
                <div className="group-h">
                  <div className="gt">
                    <span className="eyebrow">Concepts</span>
                    <b>{concepts.length === 1 ? '1 concept' : `${concepts.length} concepts`}</b>
                  </div>
                </div>
                {concepts.map((item) => (
                  <Link className="row" key={item.id} to={`/admin/items/${item.id}`}>
                    <span className="chip k-concept">Concept</span>
                    <span className="t">{item.title}</span>
                    <StatusChip item={item} />
                    <span className="m">
                      {(item.scenarios ?? []).length} {(item.scenarios ?? []).length === 1 ? 'scenario' : 'scenarios'}
                    </span>
                  </Link>
                ))}
              </section>
            )}

            {routines.length > 0 && (
              <section className="group">
                <div className="group-h">
                  <div className="gt">
                    <span className="eyebrow">Routines</span>
                    <b>{routines.length === 1 ? '1 routine' : `${routines.length} routines`}</b>
                  </div>
                </div>
                {routines.map((item) => (
                  <Link className="row" key={item.id} to={`/admin/items/${item.id}`}>
                    <span className="chip k-routine">Routine</span>
                    <span className="t">{item.title}</span>
                    <StatusChip item={item} />
                    <span className="m">
                      {(item.steps ?? []).length} {(item.steps ?? []).length === 1 ? 'step' : 'steps'}
                    </span>
                  </Link>
                ))}
              </section>
            )}

            {focus.length > 0 && (
              <section className="group">
                <div className="group-h">
                  <div className="gt">
                    <span className="eyebrow">Focus</span>
                    <b>{focus.length === 1 ? '1 focus item' : `${focus.length} focus items`}</b>
                  </div>
                </div>
                {focus.map((item) => (
                  <Link className="row" key={item.id} to={`/admin/items/${item.id}`}>
                    <span className="chip k-focus">Focus</span>
                    <span className="t">{item.title}</span>
                    <StatusChip item={item} />
                  </Link>
                ))}
              </section>
            )}
          </>
        )}

        <div className="libfoot">
          <button type="button" className="textbtn" onClick={() => setArchived((a) => !a)}>
            {archived ? 'Back to library' : 'Show archived'}
          </button>
          <button type="button" className="textbtn muted" onClick={() => void signOut()}>
            Sign out
          </button>
        </div>
      </main>
    </div>
  );
}
