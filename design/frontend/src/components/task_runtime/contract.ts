/**
 * The universal task-runtime contract.
 *
 * Every runtime view — regardless of its UI — honours this contract, so the
 * host, route, data layer, and invalidation set never change when a new view
 * is added. The body of {@link AttemptController.complete} is generic so a
 * future non-voice task type (e.g. a breathing timer posting `{ heldSeconds }`)
 * fits without touching this seam.
 */

import type { ComponentType } from 'react';
import type { CompleteTaskResult, TaskRuntime } from '@/types/models';

/** Completion body shape used by the voice family (maps to `completeTask`). */
export interface VoiceCompleteBody {
  clientTranscript?: string;
}

/** Lifecycle status of the single completion mutation. */
export type AttemptStatus = 'idle' | 'submitting' | 'success' | 'error';

/**
 * Drives the one multi-effect mutation of the runtime: completing the attempt.
 * Generic over the completion `Body` so non-voice types can post their own shape.
 */
export interface AttemptController<Body = VoiceCompleteBody> {
  complete: (body: Body) => Promise<CompleteTaskResult>;
  isSubmitting: boolean;
  result: CompleteTaskResult | null;
  status: AttemptStatus;
  /** True when the last completion exhausted today's free tier. */
  paywallOnDone: boolean;
}

/** Props every runtime view receives from the host. */
export interface TaskRuntimeViewProps<Body = VoiceCompleteBody> {
  /** The full, mapped runtime view-model (task, taskType, content, payload). */
  payload: TaskRuntime;
  attempt: AttemptController<Body>;
}

/** A full runtime view: owns its own shell, dispatched by `uiSchemaKey`. */
export type TaskRuntimeView<Body = VoiceCompleteBody> = ComponentType<
  TaskRuntimeViewProps<Body>
>;
