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

setupIonicReact();

/** Keys used for persisted client-side secrets/identifiers. */
export const STORAGE_KEYS = {
  guestToken: 'riffy.guest_session_token',
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
function buildIntegrations(): Integrations {
  const secureStore: SecureStore = new CapacitorSecureStore();
  const auth: AuthGateway = new FirebaseAuthGateway();
  // iOS/Android purchase via StoreKit/Play Billing through purchases-capacitor.
  // The web build has no in-app purchase path — the paywall points users to
  // download the app — and this gateway degrades gracefully there: configure()
  // no-ops, offerings come back empty, and purchase throws a friendly AppError.
  const subscriptions: SubscriptionGateway = new RevenueCatSubscriptionGateway();
  const analytics: AnalyticsGateway = new PostHogAnalyticsGateway();
  const device: DeviceServices = new CapacitorDeviceServices();
  const updater: AppUpdater = new CapgoUpdater();

  const tokens: TokenProvider = {
    getIdToken: () => auth.getIdToken(),
    getGuestToken: () => secureStore.get(STORAGE_KEYS.guestToken),
  };

  const http = createHttpClient({
    baseUrl: import.meta.env.VITE_API_BASE_URL,
    tokens,
  });
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
  const integrations = useMemo(() => buildIntegrations(), []);

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
