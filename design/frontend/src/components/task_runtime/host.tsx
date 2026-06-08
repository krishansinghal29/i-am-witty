/**
 * Thin dispatcher rendered by the task-runtime page. It owns nothing visual:
 * it loads the runtime payload, creates the attempt controller, and hands both
 * to the view registered for the task's `uiSchemaKey` (or a graceful fallback).
 */

import { useParams } from 'react-router-dom';
import { LoadingView, ErrorView, EmptyView } from '@/components/ui';
import { useTaskRuntime } from '@/features/task_runtime/use_task_runtime';
import { useTaskAttempt } from '@/features/task_runtime/use_task_attempt';
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
  const { data, isLoading, isError, refetch } = useTaskRuntime(taskId);
  const attempt = useTaskAttempt(data?.attemptId ?? null);

  if (isLoading) {
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
