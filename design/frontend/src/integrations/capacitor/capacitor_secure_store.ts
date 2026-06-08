import { SecureStorage } from '@aparajita/capacitor-secure-storage';

import type { SecureStore } from '@/integrations/ports/secure_store';

/**
 * Real Capacitor adapter backed by `@aparajita/capacitor-secure-storage`.
 *
 * On native platforms values are persisted to the OS keychain/keystore. Each
 * operation falls back to `localStorage` so the app remains usable on the web,
 * where the secure-storage plugin is unavailable.
 */
export class CapacitorSecureStore implements SecureStore {
  async get(key: string): Promise<string | null> {
    try {
      const v = await SecureStorage.get(key);
      if (v === null || v === undefined) {
        return null;
      }
      if (typeof v === 'string') {
        return v;
      }
      return String(v);
    } catch {
      return localStorage.getItem(key);
    }
  }

  async set(key: string, value: string): Promise<void> {
    try {
      await SecureStorage.set(key, value);
    } catch {
      localStorage.setItem(key, value);
    }
  }

  async remove(key: string): Promise<void> {
    try {
      await SecureStorage.remove(key);
    } catch {
      // Some plugin versions throw if the key is absent — swallow that and
      // mirror the removal in the web fallback store.
      localStorage.removeItem(key);
    }
  }
}
