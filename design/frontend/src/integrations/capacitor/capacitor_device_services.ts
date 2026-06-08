import { Capacitor } from '@capacitor/core';
import { PushNotifications } from '@capacitor/push-notifications';

import type {
  DeviceInfo,
  DeviceServices,
  NotificationPermission,
} from '@/integrations/ports/device_services';

const DEVICE_KEY_STORAGE_KEY = 'witty_device_key';
const PUSH_TOKEN_TIMEOUT_MS = 10_000;

/**
 * Real Capacitor adapter providing device identity, push-notification
 * permission handling, and push-token retrieval.
 */
export class CapacitorDeviceServices implements DeviceServices {
  private platform(): 'ios' | 'android' | 'web' {
    const p = Capacitor.getPlatform();
    if (p === 'ios' || p === 'android') {
      return p;
    }
    return 'web';
  }

  async getDeviceInfo(): Promise<DeviceInfo> {
    let deviceKey = localStorage.getItem(DEVICE_KEY_STORAGE_KEY);
    if (!deviceKey) {
      deviceKey = this.generateDeviceKey();
      localStorage.setItem(DEVICE_KEY_STORAGE_KEY, deviceKey);
    }

    const appVersion = import.meta.env.VITE_APP_VERSION || null;

    return {
      deviceKey,
      platform: this.platform(),
      appVersion,
    };
  }

  async requestNotificationPermission(): Promise<NotificationPermission> {
    if (!Capacitor.isNativePlatform()) {
      return 'unsupported';
    }
    const r = await PushNotifications.requestPermissions();
    return this.mapPermission(r.receive);
  }

  async getNotificationPermission(): Promise<NotificationPermission> {
    if (!Capacitor.isNativePlatform()) {
      return 'unsupported';
    }
    const r = await PushNotifications.checkPermissions();
    return this.mapPermission(r.receive);
  }

  async getPushToken(): Promise<string | null> {
    if (!Capacitor.isNativePlatform()) {
      return null;
    }

    return new Promise<string | null>((resolve) => {
      let settled = false;
      let registrationHandle: { remove: () => Promise<void> } | undefined;
      let errorHandle: { remove: () => Promise<void> } | undefined;
      let timeoutId: ReturnType<typeof setTimeout> | undefined;

      const cleanup = (): void => {
        if (timeoutId !== undefined) {
          clearTimeout(timeoutId);
        }
        void registrationHandle?.remove();
        void errorHandle?.remove();
      };

      const settle = (value: string | null): void => {
        if (settled) {
          return;
        }
        settled = true;
        cleanup();
        resolve(value);
      };

      void (async () => {
        registrationHandle = await PushNotifications.addListener(
          'registration',
          (token) => {
            settle(token.value);
          },
        );
        errorHandle = await PushNotifications.addListener(
          'registrationError',
          () => {
            settle(null);
          },
        );

        timeoutId = setTimeout(() => {
          settle(null);
        }, PUSH_TOKEN_TIMEOUT_MS);

        try {
          await PushNotifications.register();
        } catch {
          settle(null);
        }
      })();
    });
  }

  async requestInAppReview(): Promise<void> {
    // TODO: wire @capacitor-community/in-app-review when added
    return;
  }

  private mapPermission(state: string): NotificationPermission {
    if (state === 'granted') {
      return 'granted';
    }
    if (state === 'denied') {
      return 'denied';
    }
    // Covers 'prompt' and 'prompt-with-rationale'.
    return 'prompt';
  }

  private generateDeviceKey(): string {
    const c = globalThis.crypto;
    if (c && typeof c.randomUUID === 'function') {
      return c.randomUUID();
    }
    // Fallback for environments without crypto.randomUUID.
    return `witty-${Date.now().toString(36)}-${Math.random()
      .toString(36)
      .slice(2)}`;
  }
}
