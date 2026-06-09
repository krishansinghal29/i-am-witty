/**
 * Onboarding route gate for the main `/app` area.
 *
 * A user only exists once they signed in and finished onboarding, so "has a
 * session" IS "onboarded". With no session we send them to `/onboarding`.
 */

import type { ReactNode } from 'react';
import { Redirect } from 'react-router-dom';
import { IonPage, IonContent, IonSpinner } from '@ionic/react';
import { useSession } from '@/features/identity/use_session';

export function OnboardingGuard({ children }: { children: ReactNode }) {
  const { session, isLoading } = useSession();

  if (isLoading) {
    return (
      <IonPage>
        <IonContent class="ion-padding">
          <IonSpinner />
        </IonContent>
      </IonPage>
    );
  }

  if (session === null) {
    return <Redirect to="/onboarding" />;
  }

  return <>{children}</>;
}
