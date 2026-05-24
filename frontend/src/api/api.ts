const BASE_URL = (import.meta.env['VITE_API_URL'] as string | undefined) ?? 'http://localhost:8000';

export const GENERATE_QUESTION_V2_URL = `${BASE_URL}/generate_question_v2`;
export const UNIFIED_EVALUATION_URL = `${BASE_URL}/unified_evaluation`;
export const GET_RECOMMENDED_EXERCISE_URL = `${BASE_URL}/get_recommended_exercise`;
export const EXERCISE_META_URL = `${BASE_URL}/exercise_meta`;
export const GENERATE_SPRINT_QUESTION_URL = `${BASE_URL}/generate_sprint_question`;
export const ANALYZE_SPRINT_RESPONSE_URL = `${BASE_URL}/analyze_sprint_response`;
