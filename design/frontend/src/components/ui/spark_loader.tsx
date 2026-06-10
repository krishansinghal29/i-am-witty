import type { CSSProperties } from 'react';
import { useId } from 'react';
import { colors } from '@/theme/tokens';
import { RiffyMark } from './riffy_mark';
import { useReducedMotion } from './use_reduced_motion';
import './ui.css';

export type SparkLoaderVariant = 'default' | 'compact' | 'icon';

export interface SparkLoaderProps {
  variant?: SparkLoaderVariant;
  message?: string;
  ariaLabel?: string;
  className?: string;
}

const LOADER_SIZE: Record<SparkLoaderVariant, number> = {
  default: 88,
  compact: 36,
  icon: 28,
};

const MARK_SIZE: Record<SparkLoaderVariant, number> = {
  default: 46,
  compact: 20,
  icon: 16,
};

const ROOT: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: 16,
  textAlign: 'center',
};

const ROOT_COMPACT: CSSProperties = {
  ...ROOT,
  flexDirection: 'row',
  gap: 12,
  padding: 0,
};

const MESSAGE: CSSProperties = {
  fontSize: 15,
  fontWeight: 600,
  color: colors.accent,
  lineHeight: 1.45,
  letterSpacing: '-0.15px',
  maxWidth: '26ch',
  minHeight: '1.45em',
  margin: 0,
};

const MESSAGE_COMPACT: CSSProperties = {
  ...MESSAGE,
  fontSize: 13,
  textAlign: 'left',
  maxWidth: 'none',
};

function SparkRing({ gradientId, reduced }: { gradientId: string; reduced: boolean }) {
  return (
    <div
      className={reduced ? 'riffy-spark-ring' : 'riffy-spark-ring riffy-spark-ring-spin'}
      aria-hidden
    >
      <svg viewBox="0 0 100 100">
        <circle className="riffy-spark-ring-track" cx="50" cy="50" r="44" />
        <circle
          className={reduced ? 'riffy-spark-ring-track' : 'riffy-spark-ring-arc'}
          cx="50"
          cy="50"
          r="44"
          stroke={`url(#${gradientId})`}
        />
      </svg>
    </div>
  );
}

function SparkOrbit({ loaderSize, reduced }: { loaderSize: number; reduced: boolean }) {
  if (reduced) return null;

  return (
    <div
      className="riffy-spark-orbit riffy-spark-orbit-spin"
      style={{ '--loader-size': `${loaderSize}px` } as CSSProperties}
      aria-hidden
    >
      <i className="riffy-spark-dot riffy-spark-dot-primary" />
      <i className="riffy-spark-dot riffy-spark-dot-accent riffy-spark-dot-2" />
      <i className="riffy-spark-dot riffy-spark-dot-amber riffy-spark-dot-3" />
    </div>
  );
}

function SparkEqualizer({ reduced }: { reduced: boolean }) {
  if (reduced) return null;

  return (
    <div className="riffy-spark-eq" aria-hidden>
      <i />
      <i />
      <i />
      <i />
      <i />
    </div>
  );
}

/** Branded riffy loader — ring, mark, voice bars. Replaces IonSpinner crescents. */
export function SparkLoader({
  variant = 'default',
  message,
  ariaLabel,
  className,
}: SparkLoaderProps) {
  const reduced = useReducedMotion();
  const gradientId = useId().replace(/:/g, '');
  const loaderSize = LOADER_SIZE[variant];
  const markSize = MARK_SIZE[variant];
  const isCompact = variant === 'compact';
  const isIcon = variant === 'icon';
  const showOrbit = variant === 'default';
  const showEq = variant === 'default';
  const label = ariaLabel ?? message ?? 'Loading';

  const rootClass = [
    'riffy-spark-loader',
    isCompact ? 'riffy-spark-loader-compact' : '',
    isIcon ? 'riffy-spark-loader-icon' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const coreClass = [
    'riffy-spark-core',
    reduced ? 'riffy-spark-core-reduced' : 'riffy-spark-core-breathe',
    isCompact ? 'riffy-spark-core-compact' : '',
    isIcon ? 'riffy-spark-core-icon' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div
      className={rootClass}
      style={{
        ...(isCompact || isIcon ? ROOT_COMPACT : ROOT),
        '--loader-size': `${loaderSize}px`,
      } as CSSProperties}
      role="status"
      aria-busy="true"
      aria-label={label}
    >
      <svg width="0" height="0" aria-hidden="true" style={{ position: 'absolute' }}>
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={colors.primary} />
            <stop offset="55%" stopColor={colors.active} />
            <stop offset="100%" stopColor={colors.accent} />
          </linearGradient>
        </defs>
      </svg>

      <div
        className="riffy-spark-stage"
        style={{ '--loader-size': `${loaderSize}px` } as CSSProperties}
      >
        <SparkRing gradientId={gradientId} reduced={reduced} />
        {showOrbit && <SparkOrbit loaderSize={loaderSize} reduced={reduced} />}
        <div className={coreClass}>
          <RiffyMark size={markSize} className="riffy-spark-mark" />
        </div>
      </div>

      {showEq && <SparkEqualizer reduced={reduced} />}

      {message != null && message !== '' && (
        <p
          className={isCompact ? 'riffy-spark-msg riffy-spark-msg-compact' : 'riffy-spark-msg'}
          style={isCompact ? MESSAGE_COMPACT : MESSAGE}
        >
          {message}
        </p>
      )}
    </div>
  );
}
