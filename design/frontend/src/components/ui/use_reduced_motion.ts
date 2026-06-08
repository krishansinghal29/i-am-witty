import { useEffect, useState } from 'react';
import { onReducedMotionChange, prefersReducedMotion } from '@/lib/reduced_motion';

/** React hook mirroring the OS "prefers-reduced-motion" setting, live-updating. */
export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(() => prefersReducedMotion());
  useEffect(() => onReducedMotionChange(setReduced), []);
  return reduced;
}
