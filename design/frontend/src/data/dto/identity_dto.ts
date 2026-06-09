/** Wire shapes for identity endpoints (snake_case). */

/** The authenticated user returned by `POST /v1/onboarding/complete`. */
export interface LinkedUserDto {
  app_user_id: string;
  status: string;
  firebase_uid: string | null;
  timezone: string;
}
