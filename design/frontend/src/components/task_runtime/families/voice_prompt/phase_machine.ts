/**
 * Pure phase machine for the voice family.
 *
 * Flow: Brief -> Respond -> Reflect. The scaffolded view reuses the same three
 * top-level phases but inserts rehearsal stages (Push -> Pull -> Combine) inside
 * Respond, advancing the scaffold-stage index until the final, scored stage.
 *
 * This module holds no React/zustand dependency so it stays trivially testable;
 * callers apply its results to `runtime_store`.
 */

import type { RuntimePhase } from '@/state/stores/runtime_store';
import type { ScaffoldStage } from '@/types/models';

export const PHASE_ORDER: readonly RuntimePhase[] = ['brief', 'respond', 'reflect'];

export type PhaseStatus = 'done' | 'active' | 'upcoming';

export interface PhaseStep {
  key: RuntimePhase;
  label: string;
}

/** The three phase descriptors; the middle label differs for scaffolded tasks. */
export function phaseSteps(opts: { scaffolded: boolean }): PhaseStep[] {
  return [
    { key: 'brief', label: 'Brief' },
    { key: 'respond', label: opts.scaffolded ? 'Rehearse' : 'Respond' },
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

// ---------------------------------------------------------------------------
// Scaffold-stage helpers (used only when scaffold_stages is non-empty)
// ---------------------------------------------------------------------------

export function hasStages(stages: ScaffoldStage[]): boolean {
  return stages.length > 0;
}

export function clampStageIndex(stages: ScaffoldStage[], index: number): number {
  if (stages.length === 0) return 0;
  return Math.max(0, Math.min(index, stages.length - 1));
}

export function currentStage(
  stages: ScaffoldStage[],
  index: number,
): ScaffoldStage | null {
  if (stages.length === 0) return null;
  return stages[clampStageIndex(stages, index)] ?? null;
}

/**
 * Whether the stage at `index` is the final, scored stage. With no stages the
 * task is single-capture, so it is always "final".
 */
export function isFinalStage(stages: ScaffoldStage[], index: number): boolean {
  if (stages.length === 0) return true;
  const stage = currentStage(stages, index);
  if (stage?.isFinalSubmission) return true;
  return clampStageIndex(stages, index) === stages.length - 1;
}

export function nextStageIndex(stages: ScaffoldStage[], index: number): number {
  return clampStageIndex(stages, index + 1);
}
