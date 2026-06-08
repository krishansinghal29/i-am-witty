import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/react';

export function PracticePage() {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Practice</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
        <p>Practice — coming soon.</p>
      </IonContent>
    </IonPage>
  );
}
