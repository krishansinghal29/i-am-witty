import { colors } from '@/theme/tokens';

export interface RiffyMarkProps {
  /** Rendered width in px; height follows aspect ratio. */
  size: number;
  color?: string;
  className?: string;
}

/** Orange r-spark glyph from the riffy logo system. */
export function RiffyMark({ size, color = colors.accent, className }: RiffyMarkProps) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="30 18 52 54"
      aria-hidden="true"
    >
      <rect x="35.5" y="35" width="11.5" height="35" rx="5.75" fill={color} />
      <path
        d="M42 46 C45 38 52 36.5 60 40.5"
        fill="none"
        stroke={color}
        strokeWidth="11.5"
        strokeLinecap="round"
      />
      <path
        d="M70 23 C70.8 29 72.6 30.8 79 31.5 C72.6 32.2 70.8 34 70 40 C69.2 34 67.4 32.2 61 31.5 C67.4 30.8 69.2 29 70 23 Z"
        fill={color}
      />
    </svg>
  );
}
