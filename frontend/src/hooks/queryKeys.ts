export const sprintQuestionQueryKeys = {
  all: ['sprintQuestion'] as const,
  forUser: (uid: string, exerciseId: string, questionId: number) =>
    [...sprintQuestionQueryKeys.all, uid, exerciseId, questionId] as const,
  forUserAndExercise: (uid: string, exerciseId: string) =>
    [...sprintQuestionQueryKeys.all, uid, exerciseId] as const,
};
