import { GENERATE_QUESTION_V2_URL } from '@/api/api';
import { fetchWithHeaders } from '@/api/fetchWithHeaders';
import type { QuestionResponse } from '@/types/question';
import { QueryClient, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { generateQuestionQueryKeys } from './queryKeys';

const fetchQuestion = async (exerciseId: string): Promise<QuestionResponse> => {
  const response = await fetchWithHeaders(GENERATE_QUESTION_V2_URL, {
    method: 'POST',
    body: JSON.stringify({ exercise: exerciseId }),
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
};

export const useGenerateQuestion = (uid: string, exerciseId: string, questionId: number) => {
  const queryClient = useQueryClient();

  const query = useQuery<QuestionResponse>({
    queryKey: generateQuestionQueryKeys.forUser(uid, exerciseId, questionId),
    queryFn: () => fetchQuestion(exerciseId),
    enabled: !!exerciseId,
    staleTime: 60 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
    retry: 2,
  });

  useEffect(() => {
    if (query.isSuccess && query.data) {
      queryClient.invalidateQueries({
        queryKey: generateQuestionQueryKeys.forUserAndExercise(uid, exerciseId),
        predicate: q => {
          const [, , , qId] = q.queryKey;
          return typeof qId === 'number' && qId < questionId;
        },
      });
    }
  }, [query.isSuccess, query.data, queryClient, uid, exerciseId, questionId]);

  return query;
};

export const preFetchGenerateQuestion = async (
  queryClient: QueryClient,
  uid: string,
  exerciseId: string,
  questionId: number,
) => {
  if (!exerciseId) return;
  await queryClient.prefetchQuery({
    queryKey: generateQuestionQueryKeys.forUser(uid, exerciseId, questionId),
    queryFn: () => fetchQuestion(exerciseId),
    staleTime: 60 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
  });
};
