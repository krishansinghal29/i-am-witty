export interface EvaluationData {
  feedback: string;
  sample_answer: string;
}

export interface UnifiedEvaluationResponse {
  success: boolean;
  evaluation: EvaluationData;
  message?: string;
}
