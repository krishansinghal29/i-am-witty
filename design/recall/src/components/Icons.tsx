import type { ReactNode } from 'react';

interface IconProps {
  size?: number;
}

/** Orange r-spark glyph from the Riffy logo system. */
export function Mark({ size = 20 }: IconProps) {
  return (
    <svg className="mark" width={size} height={size} viewBox="30 18 52 54" aria-hidden="true">
      <rect x="35.5" y="35" width="11.5" height="35" rx="5.75" />
      <path className="arc" d="M42 46 C45 38 52 36.5 60 40.5" />
      <path d="M70 23 C70.8 29 72.6 30.8 79 31.5 C72.6 32.2 70.8 34 70 40 C69.2 34 67.4 32.2 61 31.5 C67.4 30.8 69.2 29 70 23 Z" />
    </svg>
  );
}

function Stroke({ size = 18, width = 2.2, children }: IconProps & { width?: number; children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={width}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export const CloseIcon = ({ size }: IconProps) => (
  <Stroke size={size}>
    <path d="M6 6l12 12M18 6L6 18" />
  </Stroke>
);

export const BackIcon = ({ size }: IconProps) => (
  <Stroke size={size}>
    <path d="M15 18l-6-6 6-6" />
  </Stroke>
);

export const PlusIcon = ({ size = 14 }: IconProps) => (
  <Stroke size={size} width={2.6}>
    <path d="M12 5v14M5 12h14" />
  </Stroke>
);

export const SearchIcon = ({ size = 16 }: IconProps) => (
  <Stroke size={size}>
    <circle cx="11" cy="11" r="7" />
    <path d="M20 20l-3.5-3.5" />
  </Stroke>
);

export const CheckIcon = ({ size = 12 }: IconProps) => (
  <Stroke size={size} width={3.4}>
    <path d="M5 12l5 5 9-10" />
  </Stroke>
);

export const UpIcon = ({ size = 14 }: IconProps) => (
  <Stroke size={size} width={2.4}>
    <path d="M6 15l6-6 6 6" />
  </Stroke>
);

export const DownIcon = ({ size = 14 }: IconProps) => (
  <Stroke size={size} width={2.4}>
    <path d="M6 9l6 6 6-6" />
  </Stroke>
);

export const SparkleIcon = ({ size = 14 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" />
  </svg>
);

export const MicIcon = ({ size = 16 }: IconProps) => (
  <Stroke size={size}>
    <rect x="9" y="3" width="6" height="11" rx="3" />
    <path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
  </Stroke>
);

export const LockIcon = ({ size = 12 }: IconProps) => (
  <Stroke size={size} width={2.4}>
    <rect x="5" y="11" width="14" height="10" rx="2.5" />
    <path d="M8 11V8a4 4 0 0 1 8 0v3" />
  </Stroke>
);
