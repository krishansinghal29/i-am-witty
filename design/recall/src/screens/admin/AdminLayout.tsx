/**
 * Gate for /admin. Signs the owner in with Google, then asks the backend
 * whether this account may edit (GET /v1/admin/recall/me). The backend is the
 * real guard; this only decides what to show.
 */

import { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import type { User } from 'firebase/auth';
import { getMe } from '@/api/recall';
import { ApiError, errorMessage } from '@/api/http';
import type { Me } from '@/api/types';
import { Mark } from '@/components/Icons';
import { firebaseConfigured, signInWithGoogle, signOut, subscribeAuth } from '@/lib/firebase';

type Access =
  | { state: 'checking' }
  | { state: 'ok'; me: Me }
  | { state: 'forbidden' }
  | { state: 'error'; message: string };

function Loading() {
  return (
    <div className="screen">
      <div className="loading" aria-label="Loading">
        <div className="spinner" />
      </div>
    </div>
  );
}

function signInError(error: unknown): string | null {
  const code = (error as { code?: string } | null)?.code ?? '';
  if (code === 'auth/popup-closed-by-user' || code === 'auth/cancelled-popup-request') return null;
  if (code === 'auth/popup-blocked') return 'Your browser blocked the sign-in window. Allow pop-ups for this site and try again.';
  if (code === 'auth/unauthorized-domain') {
    return "Sign-in isn't enabled for this web address yet. Add it to the authorized domains in Firebase Auth.";
  }
  return "Sign-in didn't work. Try again.";
}

function SignInScreen({ forbiddenEmail }: { forbiddenEmail?: string | null }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const forbidden = forbiddenEmail !== undefined;

  const signIn = async () => {
    setBusy(true);
    setError(null);
    try {
      await signInWithGoogle();
    } catch (e) {
      setError(signInError(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="screen">
      <main className="body">
        <div className="signin">
          <Mark size={48} />
          <h1>Recall admin</h1>
          <p>Add and edit the lines, concepts, routines and focus items that show up in practice.</p>
          {!firebaseConfigured ? (
            <div className="state" role="alert">
              <p>Sign-in isn't set up for this site yet.</p>
            </div>
          ) : forbidden ? (
            <div className="state" role="alert">
              <p>This account can't edit Recall.</p>
              {forbiddenEmail && <span className="who">Signed in as {forbiddenEmail}</span>}
              <button type="button" className="textbtn" style={{ alignSelf: 'flex-start' }} onClick={() => void signOut()}>
                Sign out
              </button>
            </div>
          ) : (
            <>
              <button type="button" className="gbtn" disabled={busy} onClick={() => void signIn()}>
                <span className="gdot" aria-hidden="true">
                  G
                </span>
                {busy ? 'Signing in…' : 'Continue with Google'}
              </button>
              {error && (
                <div className="state" role="alert">
                  <p>{error}</p>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export function AdminLayout() {
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const [access, setAccess] = useState<Access>({ state: 'checking' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => subscribeAuth(setUser), []);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    setAccess({ state: 'checking' });
    getMe()
      .then((me) => {
        if (!cancelled) setAccess({ state: 'ok', me });
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        if (error instanceof ApiError && error.status === 403) setAccess({ state: 'forbidden' });
        else setAccess({ state: 'error', message: errorMessage(error) });
      });
    return () => {
      cancelled = true;
    };
  }, [user, attempt]);

  if (user === undefined) return <Loading />;
  if (user === null) return <SignInScreen />;

  switch (access.state) {
    case 'checking':
      return <Loading />;
    case 'forbidden':
      return <SignInScreen forbiddenEmail={user.email} />;
    case 'error':
      return (
        <div className="screen">
          <main className="body" style={{ justifyContent: 'center' }}>
            <div className="banner error" role="alert">
              <span>{access.message}</span>
            </div>
            <div className="chiprow">
              <button type="button" className="btn ghost sm" onClick={() => setAttempt((n) => n + 1)}>
                Try again
              </button>
              <button type="button" className="textbtn muted" onClick={() => void signOut()}>
                Sign out
              </button>
            </div>
          </main>
        </div>
      );
    case 'ok':
      return <Outlet context={access.me} />;
  }
}
