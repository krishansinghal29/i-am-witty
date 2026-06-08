export type FeatureFlagValue = boolean | string | undefined;

export interface AnalyticsGateway {
  capture(event: string, props?: Record<string, unknown>): void;
  identify(appUserId: string, traits?: Record<string, unknown>): void;
  reset(): void;
  isFeatureEnabled(flag: string): boolean;
  getFeatureFlag(flag: string): FeatureFlagValue;
  onFeatureFlags(cb: () => void): () => void;
}
