const BASE_URL = (import.meta.env['VITE_API_URL'] as string | undefined) ?? 'http://localhost:8000';

export const GENERATE_SPRINT_QUESTION_URL = `${BASE_URL}/generate_sprint_question`;
export const ANALYZE_SPRINT_RESPONSE_URL = `${BASE_URL}/analyze_sprint_response`;
