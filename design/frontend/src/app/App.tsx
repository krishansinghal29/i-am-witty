import { IonApp } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { AppProviders } from '@/app/providers';
import { AuthGuard } from '@/app/guards/auth_guard';
import { AppRoutes } from '@/app/routes';

export default function App() {
  return (
    <AppProviders>
      <IonApp>
        <IonReactRouter>
          <AuthGuard>
            <AppRoutes />
          </AuthGuard>
        </IonReactRouter>
      </IonApp>
    </AppProviders>
  );
}
