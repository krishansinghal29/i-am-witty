export interface Exercise {
  id?: string;
  name?: string;
  title?: string[];
  examples?: Record<string, ExampleOptions[]>;
  description?: string[];
  clusters?: string[];
  primarySkills?: string[];
  version?: number;
  imageUrls?: string[];
  status?: string;
}

export interface ExampleOptions {
  role: string;
  content: string;
}

export type ExerciseIntroData = Pick<Exercise, 'id' | 'name' | 'title' | 'description' | 'imageUrls' | 'primarySkills'>;
export type ExerciseExampleData = Pick<Exercise, 'examples'>;
export type ExerciseStep = 'intro' | 'example' | 'practice' | 'feedback';

export interface GetRecommendedExerciseResponse {
  success?: boolean;
  recommendedExercise: string;
  reason: string;
}
