import { ANALYZE_SPRINT_RESPONSE_URL, GENERATE_SPRINT_QUESTION_URL } from '@/api/api';
import { fetchWithHeaders } from '@/api/fetchWithHeaders';
import type { QuestionMessage } from '@/types/question';
import { QueryClient, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { sprintQuestionQueryKeys } from './queryKeys';

export interface SprintAnalysisResult {
  success: boolean;
  feedback: string;
  sample_answer: string;
}

export interface SprintTechnique {
  name: string;
  instruction: string;
  example?: string;
}

export interface SprintQuestionResult {
  question: QuestionMessage[];
  audio_base64: string | null;
  content_type: string | null;
  speech_text: string | null;
  avatar_image_url?: string | null;
  technique?: SprintTechnique | null;
}

interface AnalyzeSprintPayload {
  transcription: string;
  audio_base64: string;
  duration_seconds: number;
  word_count: number;
  question_data: QuestionMessage[];
  exercise_type: string;
  technique_name?: string;
}

const fetchSprintQuestion = async (exercise: string): Promise<SprintQuestionResult> => {
  const response = await fetchWithHeaders(GENERATE_SPRINT_QUESTION_URL, {
    method: 'POST',
    body: JSON.stringify({ exercise }),
  });
  if (!response.ok) throw new Error(`Question request failed: ${response.status}`);
  return response.json();
};

const analyzeSprint = async (params: AnalyzeSprintPayload): Promise<SprintAnalysisResult> => {
  const response = await fetchWithHeaders(ANALYZE_SPRINT_RESPONSE_URL, {
    method: 'POST',
    body: JSON.stringify(params),
  });
  if (!response.ok) throw new Error(`Analysis request failed: ${response.status}`);
  const data = await response.json();
  if (!data.success) throw new Error(data.error || 'Analysis failed');
  return data;
};

export const useGenerateSprintQuestion = (uid: string, exerciseId: string, questionId: number, enabled = true) => {
  const queryClient = useQueryClient();

  const query = useQuery<SprintQuestionResult>({
    queryKey: sprintQuestionQueryKeys.forUser(uid, exerciseId, questionId),
    queryFn: () => fetchSprintQuestion(exerciseId),
    enabled: enabled && !!exerciseId,
    staleTime: 60 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    retry: 1,
  });

  useEffect(() => {
    if (query.isSuccess && query.data) {
      queryClient.invalidateQueries({
        queryKey: sprintQuestionQueryKeys.forUserAndExercise(uid, exerciseId),
        predicate: q => {
          const [, , , existingId] = q.queryKey;
          return typeof existingId === 'number' && existingId < questionId;
        },
      });
    }
  }, [query.isSuccess, query.data, queryClient, uid, exerciseId, questionId]);

  return query;
};

export const prefetchSprintQuestion = async (
  queryClient: QueryClient,
  uid: string,
  exerciseId: string,
  questionId: number,
) => {
  if (!exerciseId) return;
  await queryClient.prefetchQuery({
    queryKey: sprintQuestionQueryKeys.forUser(uid, exerciseId, questionId),
    queryFn: () => fetchSprintQuestion(exerciseId),
    staleTime: 60 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
  });
};

export const useAnalyzeSprintResponse = () => {
  return useMutation<SprintAnalysisResult, Error, AnalyzeSprintPayload>({
    mutationFn: analyzeSprint,
    retry: 1,
  });
};
