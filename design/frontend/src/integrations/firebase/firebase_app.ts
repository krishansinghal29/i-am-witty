/**
 * Firebase app + auth bootstrap.
 *
 * Builds the Firebase config from Vite env vars and exposes a lazily
 * initialised `Auth` singleton. Config presence is surfaced via
 * `firebaseConfigured` so callers (the auth gateway) can fail fast with a
 * friendly message when Firebase has not been wired up for the environment.
 */

import { getApp, getApps, initializeApp } from 'firebase/app';
import type { FirebaseApp, FirebaseOptions } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import type { Auth } from 'firebase/auth';

const config: FirebaseOptions = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

/**
 * True only when the minimum required Firebase config is present. The gateway
 * guards every sign-in on this flag, so an unconfigured build still type-checks
 * and runs (it just can't authenticate).
 */
export const firebaseConfigured: boolean = Boolean(
  import.meta.env.VITE_FIREBASE_API_KEY &&
    import.meta.env.VITE_FIREBASE_PROJECT_ID,
);

/**
 * Lazily initialise the Firebase app (once) and return its `Auth` instance.
 *
 * Even when `firebaseConfigured` is false this returns a constructed `Auth`;
 * it simply won't be usable. Callers must check `firebaseConfigured` before
 * attempting any sign-in.
 */
export function getFirebaseAuth(): Auth {
  const app: FirebaseApp =
    getApps().length > 0 ? getApp() : initializeApp(config);
  return getAuth(app);
}
