import { useState } from 'react';
import type { KeyboardEvent } from 'react';
import type { Cue, CueType } from '@/api/types';

interface Props {
  cues: Cue[];
  type: CueType;
  text: string;
  /** The existing cue the text resolves to, if any. */
  resolved: Cue | null;
  error?: string;
  onText: (text: string) => void;
  onPick: (cue: Cue) => void;
}

type Option = { kind: 'cue'; cue: Cue } | { kind: 'create' };

export function CueCombobox({ cues, type, text, resolved, error, onText, onPick }: Props) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);

  const q = text.trim().toLowerCase();
  const exact = cues.some((c) => c.text.trim().toLowerCase() === q);
  const options: Option[] = [
    ...cues
      .filter((c) => c.type === type && (q === '' || c.text.toLowerCase().includes(q)))
      .sort((a, b) => b.line_count - a.line_count || a.text.localeCompare(b.text))
      .slice(0, 8)
      .map((cue) => ({ kind: 'cue' as const, cue })),
    ...(q && !exact ? [{ kind: 'create' as const }] : []),
  ];
  const showList = open && options.length > 0 && !(resolved && options.length === 1);

  const choose = (option: Option) => {
    if (option.kind === 'cue') onPick(option.cue);
    setOpen(false);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setOpen(true);
      setActive((i) => Math.min(i + 1, options.length - 1));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (event.key === 'Enter' && showList) {
      event.preventDefault();
      const option = options[Math.min(active, options.length - 1)];
      if (option) choose(option);
    } else if (event.key === 'Escape') {
      setOpen(false);
    }
  };

  const activeId = showList ? `cue-option-${Math.min(active, options.length - 1)}` : undefined;

  return (
    <div className="combo">
      <input
        id="cue"
        className="input"
        role="combobox"
        aria-expanded={showList}
        aria-controls="cue-listbox"
        aria-autocomplete="list"
        aria-activedescendant={activeId}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? 'cue-error' : 'cue-help'}
        autoComplete="off"
        placeholder={type === 'reaction' ? 'What she says, e.g. You’re such a player' : 'A goal, e.g. Get her to qualify'}
        value={text}
        onChange={(e) => {
          onText(e.target.value);
          setOpen(true);
          setActive(0);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onKeyDown={onKeyDown}
      />
      {showList && (
        <ul className="listbox" id="cue-listbox" role="listbox" aria-label="Cues">
          {options.map((option, i) => (
            <li
              key={option.kind === 'cue' ? option.cue.id : 'create'}
              id={`cue-option-${i}`}
              role="option"
              aria-selected={i === active}
              className={option.kind === 'create' ? 'create' : undefined}
              onMouseDown={(e) => {
                e.preventDefault();
                choose(option);
              }}
              onMouseEnter={() => setActive(i)}
            >
              {option.kind === 'cue' ? (
                <>
                  <span className="t">{option.cue.text}</span>
                  <span className="m">
                    {option.cue.line_count} {option.cue.line_count === 1 ? 'line' : 'lines'}
                  </span>
                </>
              ) : (
                <span className="t">Create new cue: {`“${text.trim()}”`}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
