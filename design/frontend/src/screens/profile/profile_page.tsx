import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/react';

export function ProfilePage() {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Profile</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
        <p>Profile — coming soon.</p>
      </IonContent>
    </IonPage>
  );
}
