export type NotificationPermission = 'granted' | 'denied' | 'prompt' | 'unsupported';

export interface DeviceInfo {
  deviceKey: string;
  platform: 'ios' | 'android' | 'web';
  appVersion: string | null;
}

export interface DeviceServices {
  getDeviceInfo(): Promise<DeviceInfo>;
  requestNotificationPermission(): Promise<NotificationPermission>;
  getNotificationPermission(): Promise<NotificationPermission>;
  getPushToken(): Promise<string | null>;
  requestInAppReview(): Promise<void>;
}
