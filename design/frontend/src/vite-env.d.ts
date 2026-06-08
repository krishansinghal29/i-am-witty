/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_ENV: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_RELEASE_CHANNEL: string;

  readonly VITE_FIREBASE_API_KEY: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN: string;
  readonly VITE_FIREBASE_PROJECT_ID: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID: string;
  readonly VITE_FIREBASE_APP_ID: string;

  readonly VITE_POSTHOG_KEY: string;
  readonly VITE_POSTHOG_HOST: string;

  readonly VITE_REVENUECAT_IOS_KEY: string;
  readonly VITE_REVENUECAT_ANDROID_KEY: string;
  readonly VITE_REVENUECAT_WEB_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
