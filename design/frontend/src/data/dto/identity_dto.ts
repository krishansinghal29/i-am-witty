/** Wire shapes for identity / session endpoints (snake_case). */

export interface GuestSessionDto {
  app_user_id: string;
  status: string;
  session_token: string;
  timezone: string;
}

export interface LinkedUserDto {
  app_user_id: string;
  status: string;
  firebase_uid: string | null;
  timezone: string;
}
