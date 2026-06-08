import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/react';

export function TaskRuntimePage() {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Practice session</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
        <p>Practice session — coming soon.</p>
      </IonContent>
    </IonPage>
  );
}
