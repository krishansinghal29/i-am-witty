export type SprintStep = 'intro' | 'loading' | 'listening' | 'recording' | 'analyzing' | 'feedback';
export const RECORDING_LIMIT_SECONDS = 30;

export interface ScaffoldStage {
  step: string;
  instruction: string;
}

// Exercises that walk the user through guided stages before the final, graded
// response. Stages 1..n-1 are rehearsal (transcript discarded); only the last
// stage's recording is submitted for analysis.
export const SCAFFOLD_STAGES: Record<string, ScaffoldStage[]> = {
  pushPull: [
    { step: 'Step 1 of 3', instruction: 'Say just the push — one sentence, no softening' },
    { step: 'Step 2 of 3', instruction: 'Say just the genuine compliment — no irony' },
    { step: 'Step 3 of 3', instruction: 'Combine them into one push-pull line' },
  ],
  firstUnusualThing: [
    { step: 'Step 1 of 3 · Notice', instruction: 'Say the one most ordinary detail in this scene' },
    { step: 'Step 2 of 3 · Frame', instruction: 'Introduce ONE unusual thing about it — state it straight, like it’s normal' },
    { step: 'Step 3 of 3 · Associate', instruction: 'Now the full move: your unusual thing + “if that’s true, what else is true?”' },
  ],
};

export const isScaffoldedExercise = (exerciseId: string): boolean => exerciseId in SCAFFOLD_STAGES;

export const getScaffoldStageCount = (exerciseId: string): number =>
  SCAFFOLD_STAGES[exerciseId]?.length ?? 0;
