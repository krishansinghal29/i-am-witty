import type { CSSProperties, KeyboardEvent, ReactNode } from 'react';
import { colors, radius, shadows } from '@/theme/tokens';
import './ui.css';

export interface CardProps {
  children: ReactNode;
  /** When provided the card becomes pressable (button semantics + keyboard). */
  onClick?: () => void;
  padding?: number | string;
  /** Highlights the card with the primary border (e.g. a chosen option). */
  selected?: boolean;
  className?: string;
  style?: CSSProperties;
  ariaLabel?: string;
}

export function Card({
  children,
  onClick,
  padding = 16,
  selected = false,
  className,
  style,
  ariaLabel,
}: CardProps) {
  const pressable = typeof onClick === 'function';

  const base: CSSProperties = {
    background: colors.surface,
    border: `1px solid ${selected ? colors.primary : colors.line}`,
    borderRadius: radius.md,
    boxShadow: shadows.soft,
    padding: typeof padding === 'number' ? `${padding}px` : padding,
    ...style,
  };

  const handleKey = (event: KeyboardEvent<HTMLDivElement>) => {
    if (!pressable) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onClick?.();
    }
  };

  return (
    <div
      className={[pressable ? 'riffy-pressable' : '', className].filter(Boolean).join(' ') || undefined}
      style={base}
      onClick={onClick}
      onKeyDown={handleKey}
      role={pressable ? 'button' : undefined}
      tabIndex={pressable ? 0 : undefined}
      aria-label={ariaLabel}
    >
      {children}
    </div>
  );
}

/** Compact preset of {@link Card}, suited to catalog/grid tiles. */
export function Tile({ padding = 14, ...rest }: CardProps) {
  return <Card padding={padding} {...rest} />;
}
