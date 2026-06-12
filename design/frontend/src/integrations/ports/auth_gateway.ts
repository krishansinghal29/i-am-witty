import type { Session } from '@/types/models';

export interface AuthGateway {
  getSession(): Promise<Session | null>;
  getIdToken(forceRefresh?: boolean): Promise<string | null>; // current Firebase ID token for API auth
  signInWithApple(): Promise<Session>;
  signInWithGoogle(): Promise<Session>;
  signUpWithEmail(email: string, password: string): Promise<Session>;
  signInWithEmail(email: string, password: string): Promise<Session>;
  sendPasswordReset(email: string): Promise<void>;
  signOut(): Promise<void>;
}
