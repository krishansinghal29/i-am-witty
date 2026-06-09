/**
 * Real Firebase implementation of the {@link AuthGateway} port.
 *
 * Handles both web (popup) and native (Capacitor plugin, bridged into the JS
 * SDK) sign-in flows for Apple and Google, plus session/token reads used by the
 * HTTP client to authenticate every backend call.
 */

import { Capacitor } from '@capacitor/core';
import { FirebaseAuthentication } from '@capacitor-firebase/authentication';
import {
  GoogleAuthProvider,
  OAuthProvider,
  signInWithCredential,
  signInWithPopup,
  signOut as fbSignOut,
} from 'firebase/auth';

import { AppError } from '@/data/errors/app_error';
import type { AuthGateway } from '@/integrations/ports/auth_gateway';
import type { Session } from '@/types/models';

import { firebaseConfigured, getFirebaseAuth } from './firebase_app';

export class FirebaseAuthGateway implements AuthGateway {
  /**
   * Map the current Firebase user (if any) to a {@link Session}.
   *
   * Note: `appUserId` here is a placeholder equal to the Firebase uid. The
   * identity feature reconciles it with the backend `app_user_id` via
   * `POST /v1/auth/link`.
   */
  async getSession(): Promise<Session | null> {
    const user = getFirebaseAuth().currentUser;
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
    const u = getFirebaseAuth().currentUser;
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
