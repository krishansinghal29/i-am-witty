import type { TaskRuntimeViewProps } from '../contract';
import { RolePlayShell } from '@/components/roleplay/roleplay_shell';

/**
 * Roleplay task type: a live, multi-turn spoken conversation. It drives its own
 * turn loop (via {@link useAttemptTurn}) rather than the single-shot `complete`
 * controller the host passes, so the injected `attempt` controller is unused.
 */
export function RoleplayV1({ payload }: TaskRuntimeViewProps) {
  return <RolePlayShell payload={payload} />;
}
