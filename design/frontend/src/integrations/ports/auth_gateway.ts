import type { Session } from '@/types/models';

export interface AuthGateway {
  getSession(): Promise<Session | null>;
  getIdToken(): Promise<string | null>; // current Firebase ID token for API auth
  signInWithApple(): Promise<Session>;
  signInWithGoogle(): Promise<Session>;
  signOut(): Promise<void>;
}
