import { useMemo } from 'react';
import type { CSSProperties } from 'react';
import { colors } from '@/theme/tokens';
import { useReducedMotion } from './use_reduced_motion';
import './ui.css';

export interface CelebrationProps {
  show: boolean;
  label?: string;
}

const PALETTE = [colors.accent, colors.amber, colors.primary, colors.green, colors.sky];
const PIECE_COUNT = 90;

interface ConfettiPiece {
  id: number;
  left: number;
  delay: number;
  duration: number;
  color: string;
  size: number;
  rotate: number;
}

const OVERLAY: CSSProperties = {
  position: 'fixed',
  inset: 0,
  zIndex: 9999,
  pointerEvents: 'none',
  overflow: 'hidden',
  display: 'grid',
  placeItems: 'center',
};

const GLOW: CSSProperties = {
  position: 'absolute',
  inset: 0,
  background:
    'radial-gradient(60% 40% at 50% 35%, rgba(249, 115, 22, 0.18), transparent 70%)',
};

const LABEL: CSSProperties = {
  position: 'relative',
  padding: '10px 18px',
  borderRadius: 999,
  background: colors.surface,
  color: colors.accent,
  fontWeight: 800,
  fontSize: 16,
  boxShadow: '0 8px 30px -4px rgba(249, 115, 22, 0.3)',
};

/**
 * Celebration overlay. Renders falling confetti + a warm glow on a win, and
 * degrades to a calm static glow (no motion) when reduced motion is requested.
 */
export function Celebration({ show, label }: CelebrationProps) {
  const reduced = useReducedMotion();

  const pieces = useMemo<ConfettiPiece[]>(
    () =>
      Array.from({ length: PIECE_COUNT }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 0.6,
        duration: 1.8 + Math.random() * 1.6,
        color: PALETTE[i % PALETTE.length],
        size: 6 + Math.random() * 8,
        rotate: Math.random() * 360,
      })),
    [],
  );

  if (!show) return null;

  return (
    <div style={OVERLAY} aria-live="polite" role="status">
      <div className={reduced ? undefined : 'riffy-celebration-glow'} style={GLOW} />

      {!reduced &&
        pieces.map((piece) => (
          <span
            key={piece.id}
            className="riffy-confetti-piece"
            style={{
              left: `${piece.left}%`,
              top: -12,
              width: piece.size,
              height: piece.size * 0.6,
              background: piece.color,
              borderRadius: 2,
              transform: `rotate(${piece.rotate}deg)`,
              animationDuration: `${piece.duration}s`,
              animationDelay: `${piece.delay}s`,
            }}
          />
        ))}

      {label && <div style={LABEL}>{label}</div>}
    </div>
  );
}
