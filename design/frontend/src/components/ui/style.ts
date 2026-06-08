import type { CSSProperties } from 'react';

/**
 * Inline-style type that also permits CSS custom properties (`--foo`),
 * which Ionic components consume for theming (e.g. `--background`).
 */
export type StyleWithVars = CSSProperties & Record<`--${string}`, string | number>;
