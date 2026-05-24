import { EXERCISE_META_URL } from '@/api/api';
import type { Exercise } from '@/types/exercise';
import { useQuery } from '@tanstack/react-query';
import { exerciseMetaQueryKeys } from './queryKeys';

const fetchExerciseMeta = async (): Promise<Exercise[]> => {
  const res = await fetch(EXERCISE_META_URL);
  if (!res.ok) throw new Error('Failed to fetch exercise meta');
  const data = await res.json();
  return data.exercises || [];
};

export const useExerciseMeta = () => {
  return useQuery<Exercise[]>({
    queryKey: exerciseMetaQueryKeys.all,
    queryFn: fetchExerciseMeta,
    staleTime: 24 * 60 * 60 * 1000,
    gcTime: 24 * 60 * 60 * 1000,
  });
};

export const useExerciseById = (id?: string) => {
  const { data: exercises, isLoading, error } = useExerciseMeta();
  const exercise = exercises?.find(e => e.id === id);
  return { exercise, isLoading, error };
};
