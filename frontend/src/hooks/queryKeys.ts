export const generateQuestionQueryKeys = {
  all: ['generateQuestion'] as const,
  forUser: (uid: string, exerciseId: string, questionId: number) =>
    [...generateQuestionQueryKeys.all, uid, exerciseId, questionId] as const,
  forUserAndExercise: (uid: string, exerciseId: string) =>
    [...generateQuestionQueryKeys.all, uid, exerciseId] as const,
};

export const sprintQuestionQueryKeys = {
  all: ['sprintQuestion'] as const,
  forUser: (uid: string, exerciseId: string, questionId: number) =>
    [...sprintQuestionQueryKeys.all, uid, exerciseId, questionId] as const,
  forUserAndExercise: (uid: string, exerciseId: string) =>
    [...sprintQuestionQueryKeys.all, uid, exerciseId] as const,
};

export const getRecommendedExerciseQueryKeys = {
  all: ['recommendedExercise'] as const,
  forUserAndDate: (uid: string, date: string) =>
    [...getRecommendedExerciseQueryKeys.all, uid, date] as const,
};

export const evaluationQueryKeys = {
  all: ['evaluation'] as const,
  forExercise: (uid: string, exerciseId: string, question: unknown, response?: string) =>
    [...evaluationQueryKeys.all, uid, exerciseId, question, response] as const,
};

export const exerciseMetaQueryKeys = {
  all: ['exerciseMeta'] as const,
};
