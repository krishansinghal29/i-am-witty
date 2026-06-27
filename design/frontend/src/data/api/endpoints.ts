/**
 * Relative path builders for every backend /v1 endpoint.
 * No base URL — the http client prepends it.
 */

export const endpoints = {
  // Onboarding (single write at completion; creates the authenticated user)
  onboardingComplete: '/v1/onboarding/complete',

  // Config
  config: '/v1/config',

  // Home
  home: '/v1/home',

  // Catalog
  catalog: '/v1/catalog',

  // Lessons (audio lessons — separate tab, non-metered)
  lessons: '/v1/lessons',

  // Task runtime & lifecycle
  taskRuntime: (taskId: string) => `/v1/tasks/${taskId}/runtime`,
  startTask: (taskId: string) => `/v1/tasks/${taskId}/start`,
  completeTask: (attemptId: string) => `/v1/attempts/${attemptId}/complete`,
  turnAttempt: (attemptId: string) => `/v1/attempts/${attemptId}/turn`,
  nextRound: (attemptId: string) => `/v1/attempts/${attemptId}/next-round`,

  // Transcription
  transcriptionTokens: '/v1/transcription-tokens',

  // Comms
  notificationDevices: '/v1/notification-devices',
  supportMessages: '/v1/support-messages',

  // Access / entitlements
  access: '/v1/me/access',
  accessSync: '/v1/me/access/sync',
} as const;
