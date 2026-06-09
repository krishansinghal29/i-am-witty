/**
 * Guest-first bootstrap gate.
 *
 * Ensures a session (guest or authenticated) exists before the app's queries
 * fire, guaranteeing a token is available. Fails open on error so the user is
 * never locked out of the app.
 */

import type { ReactNode } from 'react';
import { IonPage, IonContent, IonSpinner } from '@ionic/react';
import { useSession } from '@/features/identity/use_session';
import { useSubscriptionIdentity } from '@/features/entitlement/use_subscription_identity';

export function AuthGuard({ children }: { children: ReactNode }) {
  const { session, isLoading } = useSession();

  // Identify the subscription SDK with the backend app_user_id once it's known.
  useSubscriptionIdentity(session?.appUserId ?? null);

  // Block the app until the first session resolves (no token yet).
  if (isLoading && !session) {
    return (
      <IonPage>
        <IonContent class="ion-padding">
          <IonSpinner />
        </IonContent>
      </IonPage>
    );
  }

  // On error we FAIL-OPEN: render children so the user is never locked out.
  return <>{children}</>;
}
