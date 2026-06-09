/**
 * Relative path builders for every backend /v1 endpoint.
 * No base URL — the http client prepends it.
 */

export const endpoints = {
  // Identity
  guestSessions: '/v1/guest-sessions',
  authLink: '/v1/auth/link',

  // Onboarding
  onboarding: '/v1/onboarding',
  onboardingAdvance: '/v1/onboarding/advance',

  // Config
  config: '/v1/config',

  // Home
  home: '/v1/home',

  // Catalog
  catalog: '/v1/catalog',

  // Task runtime & lifecycle
  taskRuntime: (taskId: string) => `/v1/tasks/${taskId}/runtime`,
  startTask: (taskId: string) => `/v1/tasks/${taskId}/start`,
  completeTask: (attemptId: string) => `/v1/attempts/${attemptId}/complete`,

  // Transcription
  transcriptionTokens: '/v1/transcription-tokens',

  // Comms
  reminders: '/v1/reminders',
  notificationDevices: '/v1/notification-devices',
  supportMessages: '/v1/support-messages',

  // Access / entitlements
  access: '/v1/me/access',
} as const;
