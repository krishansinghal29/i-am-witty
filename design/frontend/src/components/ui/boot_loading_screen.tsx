import type { CSSProperties } from 'react';
import { IonContent, IonPage } from '@ionic/react';
import { SparkLoader } from './spark_loader';

const CENTER: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100%',
  padding: '40px 24px',
};

export interface BootLoadingScreenProps {
  message?: string;
}

/** Full-screen Ionic boot shell with a centered Spark loader. */
export function BootLoadingScreen({ message = 'Starting up' }: BootLoadingScreenProps) {
  return (
    <IonPage>
      <IonContent fullscreen>
        <div style={CENTER}>
          <SparkLoader message={message} ariaLabel={message} />
        </div>
      </IonContent>
    </IonPage>
  );
}
