import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/react';

export function OnboardingFlowPage() {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Onboarding</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
        <p>Onboarding — coming soon.</p>
      </IonContent>
    </IonPage>
  );
}
