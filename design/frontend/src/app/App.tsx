import { useEffect } from 'react';
import { IonApp } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { AppProviders, useUpdater } from '@/app/providers';
import { AuthGuard } from '@/app/guards/auth_guard';
import { AppRoutes } from '@/app/routes';

/**
 * Tells Capgo the freshly-loaded bundle booted successfully. Auto-update applies
 * a new bundle on launch and ROLLS IT BACK unless this fires within
 * `appReadyTimeout` — so this must run once, early, on every boot. No-ops on web
 * and when the updater is disabled.
 */
function AppReadySignal() {
  const updater = useUpdater();
  useEffect(() => {
    void updater.notifyAppReady();
  }, [updater]);
  return null;
}

export default function App() {
  return (
    <AppProviders>
      <IonApp>
        <AppReadySignal />
        <IonReactRouter>
          <AuthGuard>
            <AppRoutes />
          </AuthGuard>
        </IonReactRouter>
      </IonApp>
    </AppProviders>
  );
}
