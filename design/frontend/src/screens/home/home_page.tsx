import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/react';

export function HomePage() {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Home</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
        <p>Home — coming soon.</p>
      </IonContent>
    </IonPage>
  );
}
