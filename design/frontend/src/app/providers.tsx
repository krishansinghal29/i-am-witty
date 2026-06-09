/**
 * Composition root for the riffy app.
 *
 * Client analog of the backend DI container: it constructs the concrete vendor
 * adapters, wires the HTTP client + typed API + query client, and exposes them
 * through React context so feature code depends on ports / the API — never on
 * the underlying SDKs.
 */

import { createContext, useContext, useMemo, useState } from 'react';
import type { JSX, ReactNode } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import type { QueryClient } from '@tanstack/react-query';
import { setupIonicReact } from '@ionic/react';

/* Ionic core + theming (light-first: NO dark palette import). */
import '@ionic/react/css/core.css';
import '@ionic/react/css/normalize.css';
import '@ionic/react/css/structure.css';
import '@ionic/react/css/typography.css';
import '@ionic/react/css/padding.css';
import '@ionic/react/css/float-elements.css';
import '@ionic/react/css/text-alignment.css';
import '@ionic/react/css/text-transformation.css';
import '@ionic/react/css/flex-utils.css';
import '@ionic/react/css/display.css';
import '@/theme/variables.css';

import { CapacitorSecureStore } from '@/integrations/capacitor/capacitor_secure_store';
import { CapacitorDeviceServices } from '@/integrations/capacitor/capacitor_device_services';
import { FirebaseAuthGateway } from '@/integrations/firebase/firebase_auth_gateway';
import { RevenueCatSubscriptionGateway } from '@/integrations/revenuecat/revenuecat_subscription_gateway';
import { PostHogAnalyticsGateway } from '@/integrations/posthog/posthog_analytics_gateway';
import { DeepgramTranscriptionGateway } from '@/integrations/transcription/deepgram_transcription_gateway';
import { CapgoUpdater } from '@/integrations/capgo/capgo_updater';
import { NoOpUpdater } from '@/integrations/capgo/no_op_updater';
import type { AppUpdater } from '@/integrations/capgo/capgo_updater';

import type {
  AuthGateway,
  SubscriptionGateway,
  AnalyticsGateway,
  DeviceServices,
  SecureStore,
  TranscriptionGateway,
} from '@/integrations/ports';

import { createHttpClient } from '@/data/api/http_client';
import type { HttpClient, TokenProvider } from '@/data/api/http_client';
import { createRiffyApi } from '@/data/api/riffy_api';
import type { RiffyApi } from '@/data/api/riffy_api';
import { createQueryClient } from '@/state/query_client';
import { queryKeys } from '@/state/query_keys';

setupIonicReact();

/** Keys used for persisted client-side identifiers. */
export const STORAGE_KEYS = {
  appUserId: 'riffy.app_user_id',
} as const;

/** The fully-wired integration graph exposed to feature code. */
export interface Integrations {
  auth: AuthGateway;
  subscriptions: SubscriptionGateway;
  analytics: AnalyticsGateway;
  device: DeviceServices;
  secureStore: SecureStore;
  transcription: TranscriptionGateway;
  updater: AppUpdater;
  http: HttpClient;
  api: RiffyApi;
}

/**
 * Construct every adapter and wire the data layer. Pure factory with no React
 * dependencies so it can be memoised for the provider's lifetime.
 */
function buildIntegrations(queryClient: QueryClient): Integrations {
  const secureStore: SecureStore = new CapacitorSecureStore();
  const auth: AuthGateway = new FirebaseAuthGateway();
  // iOS/Android purchase via StoreKit/Play Billing through purchases-capacitor.
  // The web build has no in-app purchase path — the paywall points users to
  // download the app — and this gateway degrades gracefully there: configure()
  // no-ops, offerings come back empty, and purchase throws a friendly AppError.
  const subscriptions: SubscriptionGateway = new RevenueCatSubscriptionGateway();
  const analytics: AnalyticsGateway = new PostHogAnalyticsGateway();
  const device: DeviceServices = new CapacitorDeviceServices();
  // CapgoUpdater already self-no-ops on web; the env flag lets dev/CI builds opt
  // out entirely and keeps full Capgo removal to a one-line swap here.
  const updater: AppUpdater =
    import.meta.env.VITE_CAPGO_ENABLED === 'false'
      ? new NoOpUpdater()
      : new CapgoUpdater();

  const baseUrl = import.meta.env.VITE_API_BASE_URL;

  const tokens: TokenProvider = {
    getIdToken: () => auth.getIdToken(),
  };

  // 401-recovery (Bearer-only). A 401 means the Firebase id token was rejected.
  // Force-refresh it once and let the http client replay the request; if no
  // fresh token is available, sign out and drop the persisted backend id so the
  // app falls back to onboarding (re-login). Single-flight so the parallel boot
  // queries all 401-ing share ONE recovery instead of each refreshing.
  let reauthInFlight: Promise<boolean> | null = null;
  const reauth = (): Promise<boolean> =>
    (reauthInFlight ??= (async () => {
      try {
        if ((await auth.getIdToken(true)) != null) return true;
      } catch {
        // fall through to sign-out
      }
      await auth.signOut().catch(() => {});
      await secureStore.remove(STORAGE_KEYS.appUserId);
      void queryClient.invalidateQueries({ queryKey: queryKeys.session });
      return false;
    })().finally(() => {
      reauthInFlight = null;
    }));

  const http = createHttpClient({ baseUrl, tokens, reauth });
  const api = createRiffyApi(http);

  const transcription: TranscriptionGateway = new DeepgramTranscriptionGateway({
    mintToken: () => api.mintTranscriptionToken(),
  });

  return {
    auth,
    subscriptions,
    analytics,
    device,
    secureStore,
    transcription,
    updater,
    http,
    api,
  };
}

const IntegrationsContext = createContext<Integrations | null>(null);

export function AppProviders({
  children,
}: {
  children: ReactNode;
}): JSX.Element {
  const [queryClient] = useState(() => createQueryClient());
  const integrations = useMemo(() => buildIntegrations(queryClient), [queryClient]);

  return (
    <QueryClientProvider client={queryClient}>
      <IntegrationsContext.Provider value={integrations}>
        {children}
      </IntegrationsContext.Provider>
    </QueryClientProvider>
  );
}

/** Read the integration graph; throws if used outside {@link AppProviders}. */
export function useIntegrations(): Integrations {
  const ctx = useContext(IntegrationsContext);
  if (ctx === null) {
    throw new Error('useIntegrations must be used within <AppProviders>');
  }
  return ctx;
}

export const useRiffyApi = (): RiffyApi => useIntegrations().api;
export const useAuth = (): AuthGateway => useIntegrations().auth;
export const useSubscriptions = (): SubscriptionGateway =>
  useIntegrations().subscriptions;
export const useAnalytics = (): AnalyticsGateway => useIntegrations().analytics;
export const useDevice = (): DeviceServices => useIntegrations().device;
export const useSecureStore = (): SecureStore => useIntegrations().secureStore;
export const useTranscription = (): TranscriptionGateway =>
  useIntegrations().transcription;
export const useUpdater = (): AppUpdater => useIntegrations().updater;
export const useHttpClient = (): HttpClient => useIntegrations().http;
