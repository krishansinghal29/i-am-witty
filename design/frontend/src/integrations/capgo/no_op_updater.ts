import type { AppUpdater } from '@/integrations/capgo/capgo_updater';

/**
 * Inert {@link AppUpdater} used when OTA is disabled (`VITE_CAPGO_ENABLED=false`)
 * — dev/web/CI builds, and the seam that makes fully dropping Capgo a one-file
 * swap rather than surgery.
 *
 * Note: this is NOT the operational kill switch. To stop updates on devices
 * already in the wild, flip the backend's `OTA_ENABLED` (instant, no rebuild);
 * this flag only governs the build it's compiled into.
 */
export class NoOpUpdater implements AppUpdater {
  async notifyAppReady(): Promise<void> {}
  async checkForUpdate(): Promise<void> {}
}
