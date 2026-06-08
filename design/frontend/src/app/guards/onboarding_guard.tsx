/**
 * Onboarding route gate for the main `/app` area.
 *
 * Redirects to `/onboarding` until onboarding is complete. Fails open on error
 * so a transient fetch failure never blocks access.
 */

import type { ReactNode } from 'react';
import { Redirect } from 'react-router-dom';
import { IonPage, IonContent, IonSpinner } from '@ionic/react';
import { useOnboardingState } from '@/features/onboarding/use_onboarding_state';

export function OnboardingGuard({ children }: { children: ReactNode }) {
  const { isLoading, isError, isComplete } = useOnboardingState();

  if (isLoading) {
    return (
      <IonPage>
        <IonContent class="ion-padding">
          <IonSpinner />
        </IonContent>
      </IonPage>
    );
  }

  // FAIL-OPEN: on error, render children rather than blocking the user.
  if (!isError && !isComplete) {
    return <Redirect to="/onboarding" />;
  }

  return <>{children}</>;
}
