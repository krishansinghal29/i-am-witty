export interface QuestionMessage {
  role: string;
  content: string;
}

export interface QuestionResponse {
  success?: boolean;
  question?: QuestionMessage[];
  avatar_image_url?: string;
}
