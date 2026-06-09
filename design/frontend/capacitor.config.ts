import type { CapacitorConfig } from '@capacitor/cli';
import { loadEnv } from 'vite';

/*
 * These values are read at `cap sync` time and compiled into the native binary,
 * so they only change with a new store build — that's expected for OTA config.
 * We reuse the project's .env (via Vite's loader) so there's a single source of
 * truth for the API base URL and the Capgo on/off flag.
 */
const env = loadEnv(process.env.NODE_ENV ?? 'production', process.cwd(), '');
const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:8000';
const capgoEnabled = env.VITE_CAPGO_ENABLED !== 'false';

const config: CapacitorConfig = {
  appId: 'com.iamwitty.app',
  appName: 'Riffy',
  webDir: 'dist',
  plugins: {
    // Self-hosted Capgo OTA: the updater talks to OUR backend, never Capgo's
    // cloud (statsUrl/channelUrl are emptied so no request ever hits
    // plugin.capgo.app — that's what keeps this free). Auto-update downloads in
    // the background and applies on next launch; app/App.tsx must call
    // notifyAppReady() on boot or Capgo will roll the bundle back.
    CapacitorUpdater: {
      autoUpdate: capgoEnabled,
      updateUrl: `${apiBaseUrl}/v1/ota/check`,
      statsUrl: '',
      channelUrl: '',
      appReadyTimeout: 10000,
    },
  },
};

export default config;
