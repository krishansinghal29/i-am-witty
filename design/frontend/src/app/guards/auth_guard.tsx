/**
 * Session bootstrap gate.
 *
 * Resolves the current session once on boot (Firebase + persisted backend id)
 * and configures the subscription SDK with the backend id when known. It does
 * NOT redirect — gating lives in {@link OnboardingGuard} (around `/app`) so the
 * public `/onboarding` and web pages stay reachable when there's no session.
 */

import type { ReactNode } from 'react';
import { IonPage, IonContent, IonSpinner } from '@ionic/react';
import { useLocation } from 'react-router-dom';
import { Capacitor } from '@capacitor/core';
import { useSession } from '@/features/identity/use_session';
import { useSubscriptionIdentity } from '@/features/entitlement/use_subscription_identity';

export function AuthGuard({ children }: { children: ReactNode }) {
  const { session, isLoading } = useSession();
  const location = useLocation();

  // Identify the subscription SDK with the backend app_user_id once it's known.
  useSubscriptionIdentity(session?.appUserId ?? null);

  // Public web pages need no session -- render them immediately.
  const isPublicWebPage =
    !Capacitor.isNativePlatform() &&
    (location.pathname === '/' || location.pathname === '/legal');
  if (isPublicWebPage) {
    return <>{children}</>;
  }

  // Block briefly until the first session resolve settles.
  if (isLoading) {
    return (
      <IonPage>
        <IonContent class="ion-padding">
          <IonSpinner />
        </IonContent>
      </IonPage>
    );
  }

  return <>{children}</>;
}
