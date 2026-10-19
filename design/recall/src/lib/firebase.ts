/**
 * Firebase Auth for Recall (auth only, same Firebase project as the Riffy app).
 *
 * Used only by the admin. Practice lives in the Riffy app's Recall tab.
 */

import { getApp, getApps, initializeApp } from 'firebase/app';
import type { FirebaseOptions } from 'firebase/app';
import {
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  signOut as firebaseSignOut,
} from 'firebase/auth';
import type { Auth, User } from 'firebase/auth';

const config: FirebaseOptions = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

export const firebaseConfigured: boolean = Boolean(
  import.meta.env.VITE_FIREBASE_API_KEY && import.meta.env.VITE_FIREBASE_PROJECT_ID,
);

function auth(): Auth {
  const app = getApps().length > 0 ? getApp() : initializeApp(config);
  return getAuth(app);
}

// Never let a slow or blocked Firebase hold up the page for longer than this.
const AUTH_READY_TIMEOUT_MS = 4000;

let ready: Promise<User | null> | null = null;

/** Resolves once Firebase has restored any persisted session (first auth event). */
export function authReady(): Promise<User | null> {
  if (!firebaseConfigured) return Promise.resolve(null);
  if (!ready) {
    ready = new Promise((resolve) => {
      const timer = window.setTimeout(() => resolve(auth().currentUser), AUTH_READY_TIMEOUT_MS);
      const unsubscribe = onAuthStateChanged(auth(), (user) => {
        unsubscribe();
        window.clearTimeout(timer);
        resolve(user);
      });
    });
  }
  return ready;
}

export async function currentIdToken(): Promise<string | null> {
  if (!firebaseConfigured) return null;
  await authReady();
  const user = auth().currentUser;
  return user ? user.getIdToken() : null;
}

export function subscribeAuth(callback: (user: User | null) => void): () => void {
  if (!firebaseConfigured) {
    callback(null);
    return () => {};
  }
  return onAuthStateChanged(auth(), callback);
}

export async function signInWithGoogle(): Promise<void> {
  await signInWithPopup(auth(), new GoogleAuthProvider());
}

export async function signOut(): Promise<void> {
  if (!firebaseConfigured) return;
  await firebaseSignOut(auth());
}
