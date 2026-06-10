/**
 * Thin dispatcher rendered by the task-runtime page. It owns nothing visual:
 * it loads the runtime payload, creates the attempt controller, and hands both
 * to the view registered for the task's `uiSchemaKey` (or a graceful fallback).
 */

import { useEffect, useRef } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { AppError } from '@/data/errors/app_error';
import { useFreeLimit } from '@/features/entitlement/use_free_limit';
import { useTaskRuntime } from '@/features/task_runtime/use_task_runtime';
import { useTaskAttempt } from '@/features/task_runtime/use_task_attempt';
import { LoadingView, ErrorView, EmptyView } from '@/components/ui';
import { taskRuntimeRegistry } from './registry';
import type { TaskRuntimeViewProps } from './contract';

function UnsupportedRuntime({ payload }: TaskRuntimeViewProps) {
  return (
    <EmptyView
      title="Not available yet"
      message={`This exercise type (${payload.taskType.uiSchemaKey}) isn't supported in this version.`}
    />
  );
}

export function TaskRuntimeHost() {
  const { taskId } = useParams<{ taskId: string }>();
  const history = useHistory();
  const { handlePaywallRequired } = useFreeLimit();
  const { data, isLoading, isError, error, refetch } = useTaskRuntime(taskId);
  const attempt = useTaskAttempt(data?.attemptId ?? null);
  const handledPaywallRef = useRef(false);

  const paywallBlocked =
    isError && error != null && AppError.from(error).code === 'paywall_required';

  useEffect(() => {
    if (!paywallBlocked || handledPaywallRef.current) return;
    handledPaywallRef.current = true;
    handlePaywallRequired(error);
    history.goBack();
  }, [paywallBlocked, error, handlePaywallRequired, history]);

  if (isLoading || paywallBlocked) {
    return <LoadingView message="Setting up your practice…" />;
  }

  if (isError || !data) {
    return (
      <ErrorView
        title="Couldn’t start this practice"
        message="We couldn’t load this exercise just now. Give it another try."
        onRetry={refetch}
      />
    );
  }

  const View = taskRuntimeRegistry[data.taskType.uiSchemaKey] ?? UnsupportedRuntime;
  return <View payload={data} attempt={attempt} />;
}
