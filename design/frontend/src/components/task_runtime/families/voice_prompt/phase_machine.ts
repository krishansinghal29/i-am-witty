/**
 * Pure phase machine for the voice family.
 *
 * Flow: Brief -> Respond -> Reflect.
 *
 * This module holds no React/zustand dependency so it stays trivially testable;
 * callers apply its results to `runtime_store`.
 */

import type { RuntimePhase } from '@/state/stores/runtime_store';

export const PHASE_ORDER: readonly RuntimePhase[] = ['brief', 'respond', 'reflect'];

export type PhaseStatus = 'done' | 'active' | 'upcoming';

export interface PhaseStep {
  key: RuntimePhase;
  label: string;
}

/** The three phase descriptors. */
export function phaseSteps(): PhaseStep[] {
  return [
    { key: 'brief', label: 'Brief' },
    { key: 'respond', label: 'Respond' },
    { key: 'reflect', label: 'Reflect' },
  ];
}

export function phaseIndex(phase: RuntimePhase): number {
  const i = PHASE_ORDER.indexOf(phase);
  return i < 0 ? 0 : i;
}

export function nextPhase(phase: RuntimePhase): RuntimePhase {
  return PHASE_ORDER[Math.min(phaseIndex(phase) + 1, PHASE_ORDER.length - 1)];
}

export function prevPhase(phase: RuntimePhase): RuntimePhase {
  return PHASE_ORDER[Math.max(phaseIndex(phase) - 1, 0)];
}

export function phaseStatus(step: RuntimePhase, current: RuntimePhase): PhaseStatus {
  const a = phaseIndex(step);
  const b = phaseIndex(current);
  if (a < b) return 'done';
  if (a === b) return 'active';
  return 'upcoming';
}
