import { UNIFIED_EVALUATION_URL } from '@/api/api';
import { fetchWithHeaders } from '@/api/fetchWithHeaders';
import type { UnifiedEvaluationResponse } from '@/types/evaluation';
import { useQuery } from '@tanstack/react-query';
import { evaluationQueryKeys } from './queryKeys';

const evaluateResponse = async (
  exerciseId: string,
  question: unknown,
  response?: string,
): Promise<UnifiedEvaluationResponse> => {
  const apiResponse = await fetchWithHeaders(UNIFIED_EVALUATION_URL, {
    method: 'POST',
    body: JSON.stringify({ exercise: exerciseId, question, response }),
  });

  if (!apiResponse.ok) throw new Error(`API error: ${apiResponse.status}`);
  const data = await apiResponse.json();

  if (!data.success) throw new Error(data.message || 'Evaluation failed');
  if (!data.evaluation?.feedback) throw new Error('No feedback received');

  return {
    success: true,
    evaluation: {
      feedback: data.evaluation.feedback,
      sample_answer: data.evaluation.sample_answer,
    },
  };
};

export const useEvaluateResponse = (uid: string, exerciseId: string, question: unknown, response?: string) => {
  return useQuery<UnifiedEvaluationResponse>({
    queryKey: evaluationQueryKeys.forExercise(uid, exerciseId, question, response),
    queryFn: () => evaluateResponse(exerciseId, question, response),
    enabled: !!exerciseId && !!question,
    staleTime: 0,
    gcTime: 5 * 60 * 1000,
    retry: 1,
  });
};
