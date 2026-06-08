import type { CSSProperties } from 'react';
import { colors } from '@/theme/tokens';

export interface TintedThumbnailProps {
  /** Slug used both to look up an asset (none exist yet) and to derive the tint. */
  keyName: string;
  title?: string;
  /** Square edge length in px. */
  size?: number;
}

const TINTS: readonly string[] = [
  colors.primary,
  colors.accent,
  colors.green,
  colors.sky,
  colors.amber,
  colors.active,
];

function hashString(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function hexToRgba(hex: string, alpha: number): string {
  const clean = hex.replace('#', '');
  const r = parseInt(clean.slice(0, 2), 16);
  const g = parseInt(clean.slice(2, 4), 16);
  const b = parseInt(clean.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function glyphFor(title: string | undefined, keyName: string): string {
  const source = (title ?? keyName.replace(/[-_]+/g, ' ')).trim();
  const words = source.split(/\s+/).filter(Boolean);
  if (words.length === 0) return '?';
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

/**
 * Placeholder task thumbnail. There are no real image assets yet, so this
 * renders a deterministic warm tint derived from `keyName` with the task's
 * initials, ready to be swapped for a real `<img>` when assets land.
 */
export function TintedThumbnail({ keyName, title, size = 62 }: TintedThumbnailProps) {
  const tint = TINTS[hashString(keyName) % TINTS.length];

  const style: CSSProperties = {
    width: size,
    height: size,
    flex: 'none',
    borderRadius: Math.round(size * 0.29),
    background: `linear-gradient(150deg, ${hexToRgba(tint, 0.2)}, ${hexToRgba(tint, 0.08)})`,
    border: `1px solid ${hexToRgba(tint, 0.28)}`,
    color: tint,
    display: 'grid',
    placeItems: 'center',
    fontWeight: 800,
    fontSize: Math.round(size * 0.32),
    letterSpacing: '0.5px',
  };

  return (
    <div style={style} role="img" aria-label={title ?? keyName}>
      {glyphFor(title, keyName)}
    </div>
  );
}
