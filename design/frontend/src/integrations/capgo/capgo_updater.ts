import { CapacitorUpdater } from '@capgo/capacitor-updater';
import { Capacitor } from '@capacitor/core';

/**
 * Thin wrapper around Capgo's over-the-air updater.
 *
 * The actual update channel / endpoints / auto-update behavior are configured
 * in `capacitor.config` and in the Capgo dashboard; this wrapper only drives
 * the manual best-effort hooks the app needs.
 */
export interface AppUpdater {
  /**
   * Call once after the web layer has booted, so Capgo doesn't roll back the
   * freshly applied bundle.
   */
  notifyAppReady(): Promise<void>;
  /**
   * Best-effort background update check/apply. Never throws.
   */
  checkForUpdate(): Promise<void>;
}

export class CapgoUpdater implements AppUpdater {
  async notifyAppReady(): Promise<void> {
    if (!Capacitor.isNativePlatform()) {
      return;
    }

    try {
      await CapacitorUpdater.notifyAppReady();
    } catch {
      // OTA must never crash the app: swallow native errors.
    }
  }

  async checkForUpdate(): Promise<void> {
    if (!Capacitor.isNativePlatform()) {
      return;
    }

    try {
      const latest = await CapacitorUpdater.getLatest();

      // A new bundle is available only when the server returns a download URL.
      if (!latest.url) {
        return;
      }

      const next = await CapacitorUpdater.download({
        url: latest.url,
        version: latest.version,
      });

      // `set` expects the downloaded bundle's id (not its version).
      await CapacitorUpdater.set({ id: next.id });
    } catch {
      // Best-effort: swallow any failure (no update, network, plugin, etc.).
    }
  }
}
