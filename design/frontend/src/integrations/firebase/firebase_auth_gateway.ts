/**
 * Real Firebase implementation of the {@link AuthGateway} port.
 *
 * Handles both web (popup) and native (Capacitor plugin, bridged into the JS
 * SDK) sign-in flows for Apple and Google, plus session/token reads used by the
 * HTTP client to authenticate every backend call.
 */

import { Capacitor } from '@capacitor/core';
import { FirebaseAuthentication } from '@capacitor-firebase/authentication';
import { FirebaseError } from 'firebase/app';
import {
  GoogleAuthProvider,
  OAuthProvider,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  signInWithCredential,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut as fbSignOut,
} from 'firebase/auth';

import { AppError } from '@/data/errors/app_error';
import type { AuthGateway } from '@/integrations/ports/auth_gateway';
import type { Session } from '@/types/models';

import { firebaseConfigured, getFirebaseAuth } from './firebase_app';

export class FirebaseAuthGateway implements AuthGateway {
  /**
   * Firebase restores persisted auth asynchronously on page load. `currentUser`
   * is null until that finishes, so every read must wait for the initial state.
   */
  private async currentUser() {
    const auth = getFirebaseAuth();
    await auth.authStateReady();
    return auth.currentUser;
  }

  /**
   * Map the current Firebase user (if any) to a {@link Session}.
   *
   * Note: `appUserId` here is a placeholder equal to the Firebase uid. The
   * identity feature reconciles it with the backend `app_user_id` via
   * `POST /v1/auth/link`.
   */
  async getSession(): Promise<Session | null> {
    const user = await this.currentUser();
    if (!user) return null;
    return {
      appUserId: user.uid,
      status: 'authenticated',
      firebaseUid: user.uid,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    };
  }

  /** Current Firebase ID token, used by the HTTP client on every call. */
  async getIdToken(forceRefresh = false): Promise<string | null> {
    const u = await this.currentUser();
    return u ? await u.getIdToken(forceRefresh) : null;
  }

  async signInWithGoogle(): Promise<Session> {
    this.assertConfigured();
    if (Capacitor.isNativePlatform()) {
      const r = await FirebaseAuthentication.signInWithGoogle();
      const cred = GoogleAuthProvider.credential(r.credential?.idToken);
      await signInWithCredential(getFirebaseAuth(), cred);
    } else {
      await signInWithPopup(getFirebaseAuth(), new GoogleAuthProvider());
    }
    return (await this.getSession())!;
  }

  async signInWithApple(): Promise<Session> {
    this.assertConfigured();
    if (Capacitor.isNativePlatform()) {
      const r = await FirebaseAuthentication.signInWithApple();
      const provider = new OAuthProvider('apple.com');
      const cred = provider.credential({
        idToken: r.credential?.idToken,
        rawNonce: r.credential?.nonce,
      });
      await signInWithCredential(getFirebaseAuth(), cred);
    } else {
      const provider = new OAuthProvider('apple.com');
      await signInWithPopup(getFirebaseAuth(), provider);
    }
    return (await this.getSession())!;
  }

  /**
   * Email/password sign-up. Unlike OAuth, email/password runs entirely through
   * the JS SDK on every platform (no native UI to bridge): the SDK persists the
   * session in the Capacitor webview, which is exactly what `getSession` /
   * `getIdToken` read.
   */
  async signUpWithEmail(email: string, password: string): Promise<Session> {
    this.assertConfigured();
    try {
      await createUserWithEmailAndPassword(getFirebaseAuth(), email, password);
    } catch (e) {
      throw mapFirebaseAuthError(e);
    }
    return (await this.getSession())!;
  }

  async signInWithEmail(email: string, password: string): Promise<Session> {
    this.assertConfigured();
    try {
      await signInWithEmailAndPassword(getFirebaseAuth(), email, password);
    } catch (e) {
      throw mapFirebaseAuthError(e);
    }
    return (await this.getSession())!;
  }

  async sendPasswordReset(email: string): Promise<void> {
    this.assertConfigured();
    try {
      await sendPasswordResetEmail(getFirebaseAuth(), email);
    } catch (e) {
      throw mapFirebaseAuthError(e);
    }
  }

  async signOut(): Promise<void> {
    if (Capacitor.isNativePlatform()) {
      await FirebaseAuthentication.signOut();
    }
    await fbSignOut(getFirebaseAuth());
  }

  /** Fail fast with a friendly message when Firebase isn't configured. */
  private assertConfigured(): void {
    if (!firebaseConfigured) {
      throw new AppError({
        code: 'unknown',
        userMessage: 'Sign-in is not configured yet.',
        reason: 'auth_unconfigured',
      });
    }
  }
}

/**
 * Translate a Firebase auth error into a user-facing {@link AppError}.
 *
 * Firebase reports failures as `FirebaseError` with an `auth/*` code; we map the
 * handful users actually hit to friendly copy and pass everything else through
 * `AppError.from` as a generic error.
 */
function mapFirebaseAuthError(e: unknown): AppError {
  const code = e instanceof FirebaseError ? e.code : '';
  switch (code) {
    case 'auth/email-already-in-use':
      return new AppError({
        code: 'conflict',
        userMessage: 'That email is already registered — try logging in.',
        reason: code,
        cause: e,
      });
    case 'auth/invalid-email':
      return new AppError({
        code: 'validation',
        userMessage: 'Enter a valid email address.',
        reason: code,
        cause: e,
      });
    case 'auth/weak-password':
      return new AppError({
        code: 'validation',
        userMessage: 'Use at least 6 characters for your password.',
        reason: code,
        cause: e,
      });
    // Email-enumeration protection collapses wrong-password / no-account into
    // one generic code; the legacy codes are kept for older SDK behaviour.
    case 'auth/invalid-credential':
    case 'auth/wrong-password':
    case 'auth/user-not-found':
      return new AppError({
        code: 'unauthorized',
        userMessage: 'Email or password is incorrect.',
        reason: code,
        cause: e,
      });
    case 'auth/user-disabled':
      return new AppError({
        code: 'forbidden',
        userMessage: 'This account has been disabled.',
        reason: code,
        cause: e,
      });
    case 'auth/too-many-requests':
      return new AppError({
        code: 'unknown',
        userMessage: 'Too many attempts — please try again shortly.',
        reason: code,
        cause: e,
      });
    case 'auth/network-request-failed':
      return new AppError({ code: 'network', reason: code, cause: e });
    default:
      return AppError.from(e);
  }
}
